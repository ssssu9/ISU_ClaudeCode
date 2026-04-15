from fastapi import APIRouter
from typing import Optional
from collections import defaultdict
import json
import os

router = APIRouter()

DATA_FILE = os.getenv("DATA_FILE_PATH", "data/expenses.json")


def _load() -> list:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
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
