import pytest
from models.models import UserInput, Investment

def test_user_input_validation():
    data = {
        "income": 5000,
        "expenses": 3000,
        "savings": 1000,
        "investments": [{"type": "stocks", "amount": 2000}],
        "goals": ["retirement"]
    }
    user_input = UserInput(**data)
    assert user_input.income == 5000

def test_invalid_input():
    data = {
        "income": -100,
        "expenses": 3000,
        "savings": 1000,
        "investments": [],
        "goals": []
    }
    try:
        UserInput(**data)
        assert False
    except ValueError:
        assert True