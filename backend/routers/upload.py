from fastapi import APIRouter, UploadFile, File, HTTPException
from services.ocr import parse_receipt

router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload")
async def upload_receipt(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="JPG, PNG, PDF 파일만 업로드 가능합니다.")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기는 10MB 이하여야 합니다.")

    try:
        result = await parse_receipt(contents, file.content_type, file.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR 파싱 실패: {str(e)}")
