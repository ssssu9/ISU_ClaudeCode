import json
import os
from typing import Optional
from datetime import date

from fastapi import APIRouter, HTTPException

router = APIRouter()


def _data_file() -> str:
    return os.getenv("DATA_FILE_PATH", "backend/data/expenses.json")


def _load() -> list:
    path = _data_file()
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: list) -> None:
    path = _data_file()
    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
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
