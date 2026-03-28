from models.models import UserInput, State
from typing import Optional

class DataIntakeAgent:
    def process(self, data: dict) -> Optional[UserInput]:
        try:
            user_input = UserInput(**data)
            # Basic validation
            if user_input.income <= 0:
                raise ValueError("Income must be positive")
            if user_input.expenses < 0:
                raise ValueError("Expenses cannot be negative")
            if user_input.savings < 0:
                raise ValueError("Savings cannot be negative")
            for inv in user_input.investments:
                if inv.amount < 0:
                    raise ValueError("Investment amounts cannot be negative")
            return user_input
        except Exception as e:
            raise ValueError(f"Invalid input data: {str(e)}")