import sys
import os

# 'uvicorn backend.main:app' 실행 시 backend/ 디렉터리를 sys.path에 추가
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()  # 라우터 임포트 전에 실행해야 모듈 레벨 환경변수가 적용됨

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import upload, expenses, summary

app = FastAPI(title="Receipt Expense Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(summary.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Receipt Expense Tracker API"}
