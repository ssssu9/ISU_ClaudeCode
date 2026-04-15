import base64
import io
import json
import os
import uuid
from datetime import datetime, timezone

from PIL import Image
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage, SystemMessage

DATA_FILE = os.getenv("DATA_FILE_PATH", "data/expenses.json")

SYSTEM_PROMPT = """당신은 영수증 OCR 전문 AI입니다.
영수증 이미지를 분석하여 반드시 아래 JSON 형식으로만 응답하세요. 설명이나 마크다운 없이 JSON만 출력하세요.

{
  "store_name": "가게명 (문자열)",
  "receipt_date": "YYYY-MM-DD (날짜, 없으면 null)",
  "receipt_time": "HH:MM (시각, 없으면 null)",
  "category": "식료품|외식|교통|쇼핑|의료|기타 중 하나",
  "items": [
    {"name": "품목명", "quantity": 1, "unit_price": 0, "total_price": 0}
  ],
  "subtotal": 0,
  "discount": 0,
  "tax": 0,
  "total_amount": 0,
  "payment_method": "결제수단 (없으면 null)"
}"""


def _to_base64(contents: bytes, content_type: str) -> str:
    if content_type == "application/pdf":
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(contents, first_page=1, last_page=1)
        buf = io.BytesIO()
        images[0].save(buf, format="JPEG")
        return base64.b64encode(buf.getvalue()).decode()

    img = Image.open(io.BytesIO(contents))
    if img.mode != "RGB":
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()


def _append_to_file(expense: dict) -> None:
    os.makedirs(os.path.dirname(DATA_FILE) if os.path.dirname(DATA_FILE) else ".", exist_ok=True)
    expenses = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            expenses = json.load(f)
    expenses.append(expense)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(expenses, f, ensure_ascii=False, indent=2)


async def parse_receipt(contents: bytes, content_type: str, filename: str) -> dict:
    image_b64 = _to_base64(contents, content_type)

    llm = ChatUpstage(
        model="solar-pro",
        api_key=os.getenv("UPSTAGE_API_KEY"),
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=[
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
            },
            {"type": "text", "text": "위 영수증의 내용을 JSON 형식으로 추출해주세요."},
        ]),
    ]

    response = await llm.ainvoke(messages)
    parsed = json.loads(response.content.strip())

    expense = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "raw_image_path": f"uploads/{filename}",
        **parsed,
    }

    _append_to_file(expense)
    return expense
