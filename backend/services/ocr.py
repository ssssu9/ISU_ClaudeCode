import json
import os
import uuid
from datetime import datetime, timezone

import httpx
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage, SystemMessage

UPSTAGE_OCR_URL = "https://api.upstage.ai/v1/document-digitization"

SYSTEM_PROMPT = """당신은 영수증 분석 전문 AI입니다.
아래에 제공된 영수증 텍스트를 분석하여 반드시 아래 JSON 형식으로만 응답하세요.
마크다운 코드블록 없이 순수 JSON 텍스트만 출력하세요.

{
  "store_name": "가게명 (문자열, 필수)",
  "receipt_date": "YYYY-MM-DD (없으면 null)",
  "receipt_time": "HH:MM (없으면 null)",
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


async def _ocr_extract(contents: bytes, filename: str) -> str:
    """Upstage Document Digitization API로 영수증 텍스트 추출 (Step 1)"""
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise ValueError("UPSTAGE_API_KEY 환경변수가 설정되지 않았습니다.")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            UPSTAGE_OCR_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            files={"document": (filename, contents)},
            data={"model": "document-parse"},
        )
        response.raise_for_status()
        data = response.json()

    # document-parse 응답: content.markdown > content.text > elements 순으로 추출
    content = data.get("content", {})
    text = content.get("markdown") or content.get("text") or ""
    if not text:
        elements = data.get("elements", [])
        text = "\n".join(
            e.get("content", {}).get("text", "") for e in elements
        )
    return text.strip()


def _parse_llm_json(raw: str) -> dict:
    """LLM 응답에서 JSON 추출 (```json ... ``` 코드블록 처리 포함)"""
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        inner = lines[1:]
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        raw = "\n".join(inner)
    return json.loads(raw.strip())


def _append_to_file(expense: dict) -> None:
    data_file = os.getenv("DATA_FILE_PATH", "backend/data/expenses.json")
    dir_path = os.path.dirname(data_file)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    expenses = []
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            expenses = json.load(f)
    expenses.append(expense)
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(expenses, f, ensure_ascii=False, indent=2)


async def parse_receipt(contents: bytes, content_type: str, filename: str) -> dict:
    # Step 1: Upstage Document Digitization API로 OCR 텍스트 추출
    ocr_text = await _ocr_extract(contents, filename)
    if not ocr_text:
        raise ValueError("영수증에서 텍스트를 추출할 수 없습니다. 이미지 품질을 확인하세요.")

    # Step 2: ChatUpstage (solar-pro)로 구조화 JSON 추출
    llm = ChatUpstage(
        model="solar-pro",
        api_key=os.getenv("UPSTAGE_API_KEY"),
    )
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"다음은 영수증에서 추출된 텍스트입니다:\n\n{ocr_text}\n\n"
                "이 내용을 JSON 형식으로 추출해주세요."
            )
        ),
    ]

    response = await llm.ainvoke(messages)
    parsed = _parse_llm_json(response.content)

    expense = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "raw_image_path": f"uploads/{filename}",
        **parsed,
    }

    _append_to_file(expense)
    return expense
