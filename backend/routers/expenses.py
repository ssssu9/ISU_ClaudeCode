from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import date
import json
import os

router = APIRouter()

DATA_FILE = os.getenv("DATA_FILE_PATH", "data/expenses.json")


def _load() -> list:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: list) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@router.get("/expenses")
def get_expenses(from_date: Optional[date] = None, to_date: Optional[date] = None):
    expenses = _load()
    if from_date:
        expenses = [e for e in expenses if e.get("receipt_date", "") >= str(from_date)]
    if to_date:
        expenses = [e for e in expenses if e.get("receipt_date", "") <= str(to_date)]
    return expenses


@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str):
    expenses = _load()
    filtered = [e for e in expenses if e["id"] != expense_id]
    if len(filtered) == len(expenses):
        raise HTTPException(status_code=404, detail="해당 지출 항목을 찾을 수 없습니다.")
    _save(filtered)
    return {"message": "삭제 완료"}


@router.put("/expenses/{expense_id}")
def update_expense(expense_id: str, body: dict):
    expenses = _load()
    for i, e in enumerate(expenses):
        if e["id"] == expense_id:
            expenses[i] = {**e, **body, "id": expense_id}
            _save(expenses)
            return expenses[i]
    raise HTTPException(status_code=404, detail="해당 지출 항목을 찾을 수 없습니다.")
