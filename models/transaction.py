from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    user_id: int
    type: str  # 'income' or 'expense'
    amount: float
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None

    def __post_init__(self):
        if self.date is None:
            self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@dataclass
class Category:
    user_id: int
    name: str
    type: str  # 'income' or 'expense'

@dataclass
class MonthlyStats:
    user_id: int
    year: int
    month: int
    total_income: float
    total_expense: float

    @property
    def balance(self) -> float:
        return self.total_income - self.total_expense 