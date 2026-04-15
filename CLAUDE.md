# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 프로젝트 개요

영수증(JPG, PNG, PDF)을 업로드하면 **Upstage Vision LLM**이 내용을 자동 파싱하여 지출 데이터로 변환·저장하는 경량 웹앱. DB 없이 JSON 파일 기반으로 동작하며 Vercel에 배포한다.

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| 프론트엔드 | React v18+, Vite v5+, TailwindCSS v3+, Axios v1+ |
| 백엔드 | Python FastAPI v0.111+, LangChain v0.2+ |
| OCR LLM | Upstage Document AI (`document-digitization-vision`) |
| 파일 처리 | Pillow, pdf2image |
| 데이터 저장 | `expenses.json` (DB 없음) |
| 배포 | Vercel (프론트 정적 빌드 + 백엔드 서버리스) |

---

## 디렉토리 구조

```
receipt-tracker/
├── frontend/
│   ├── src/
│   │   ├── pages/          # Dashboard, UploadPage, ExpenseDetail
│   │   ├── components/     # ExpenseCard, DropZone, ParsePreview, Modal, Toast 등
│   │   └── api/            # Axios 인스턴스 및 API 호출 함수
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── main.py             # FastAPI 앱 진입점
│   ├── routers/            # 라우터 모듈 (upload, expenses, summary)
│   ├── services/           # LangChain + Upstage OCR 로직
│   ├── data/
│   │   └── expenses.json   # 지출 데이터 파일
│   └── requirements.txt
├── vercel.json
└── images/                 # 샘플 영수증 이미지 (테스트용)
```

---

## 개발 명령어

### 백엔드

```bash
# 가상환경 생성 및 의존성 설치
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# 개발 서버 실행 (루트에서)
uvicorn backend.main:app --reload --port 8000
```

### 프론트엔드

```bash
cd frontend
npm install
npm run dev        # 개발 서버 (기본 포트 5173)
npm run build      # Vercel 배포용 정적 빌드
npm run preview    # 빌드 결과물 로컬 미리보기
```

### 환경변수 설정

`.env` 파일(프로젝트 루트) 또는 Vercel 환경변수에 설정:

```
UPSTAGE_API_KEY=your_key_here
VITE_API_BASE_URL=http://localhost:8000   # 로컬 개발 시
DATA_FILE_PATH=backend/data/expenses.json
```

> **주의**: `.env` 파일은 절대 커밋하지 않는다. Vercel 환경변수로만 관리한다.

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/api/upload` | 영수증 업로드 및 OCR 파싱 (`multipart/form-data`) |
| `GET` | `/api/expenses` | 전체 지출 목록 조회 (`?from=&to=` 날짜 필터) |
| `DELETE` | `/api/expenses/{id}` | 지출 항목 삭제 |
| `PUT` | `/api/expenses/{id}` | 지출 항목 수정 |
| `GET` | `/api/summary` | 지출 통계 (`?month=YYYY-MM`) |

---

## 핵심 데이터 스키마 (`expenses.json`)

```json
{
  "id": "uuid-v4",
  "created_at": "ISO8601",
  "store_name": "string",
  "receipt_date": "YYYY-MM-DD",
  "receipt_time": "HH:MM",
  "category": "string",
  "items": [{ "name": "string", "quantity": 0, "unit_price": 0, "total_price": 0 }],
  "subtotal": 0,
  "discount": 0,
  "tax": 0,
  "total_amount": 0,
  "payment_method": "string",
  "raw_image_path": "string"
}
```

---

## LangChain OCR 처리 흐름

```
파일 업로드 → PIL/pdf2image로 이미지 전처리 → Base64 인코딩
→ ChatUpstage(Vision LLM) 호출 (System: "JSON 형식으로만 응답")
→ LangChain Output Parser로 구조화
→ expenses.json에 append 저장
```

---

## 아키텍처 상 주요 제약사항

### Vercel 서버리스 데이터 영속성 문제

Vercel 서버리스 함수는 요청마다 새 컨테이너가 실행되어 `expenses.json`이 유지되지 않는다.  
MVP 단계에서는 아래 방안 중 하나를 선택한다:

| 방안 | 난이도 | 설명 |
|------|--------|------|
| 클라이언트 `localStorage` 병행 저장 | 쉬움 | 프론트에서 영속성 유지 |
| Railway / Render 배포 | 보통 | 일반 서버에서 파일 시스템 유지 |
| Vercel KV (Redis) | 보통 | Vercel 내장 키-값 저장소 |
| Supabase 무료 플랜 | 어려움 | PostgreSQL DB 전환 |

### 파일 업로드 제약

- 지원 형식: JPG, PNG, PDF만 허용
- 최대 크기: 10MB
- 서버 측 유효성 검사 필수

---

## Vercel 배포 설정 (`vercel.json`)

```json
{
  "builds": [
    { "src": "frontend/package.json", "use": "@vercel/static-build" },
    { "src": "backend/main.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "backend/main.py" },
    { "src": "/(.*)", "dest": "frontend/dist/$1" }
  ]
}
```
