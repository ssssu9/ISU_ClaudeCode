import json
import os
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter

router = APIRouter()


def _data_file() -> str:
    return os.getenv("DATA_FILE_PATH", "backend/data/expenses.json")


def _load() -> list:
    path = _data_file()
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/summary")
def get_summary(month: Optional[str] = None):
    expenses = _load()

    if month:
        expenses = [e for e in expenses if e.get("receipt_date", "").startswith(month)]

    total = sum(e.get("total_amount", 0) for e in expenses)
    by_category: dict = defaultdict(float)
    for e in expenses:
        cat = e.get("category") or "기타"
        by_category[cat] += e.get("total_amount", 0)

    return {
        "total_amount": total,
        "count": len(expenses),
        "by_category": dict(by_category),
    }
