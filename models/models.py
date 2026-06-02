from pydantic import BaseModel, field_validator
from typing import List, Optional, TypedDict

class Investment(BaseModel):
    type: str
    amount: float

    @field_validator('amount')
    def amount_non_negative(cls, v):
        if v < 0:
            raise ValueError('investment amount must be non-negative')
        return v

class UserInput(BaseModel):
    income: float
    expenses: float
    savings: float
    investments: List[Investment]
    goals: List[str]

    @field_validator('income')
    def income_positive(cls, v):
        if v <= 0:
            raise ValueError('income must be positive')
        return v

    @field_validator('expenses', 'savings')
    def non_negative(cls, v):
        if v < 0:
            raise ValueError('expenses and savings must be non-negative')
        return v

class AnalysisResult(BaseModel):
    savings_rate: float
    risk_level: str
    issues: List[str]

class FinancialPlan(BaseModel):
    summary: str
    issues: List[str]
    financial_plan: str
    recommended_actions: List[str]
    risk_level: str
    explanation: str

class State(TypedDict):
    user_input: Optional[UserInput]
    analysis: Optional[AnalysisResult]
    strategy: Optional[str]
    compliance_check: Optional[bool]
    actions: Optional[List[str]]
    final_output: Optional[FinancialPlan]
    error: Optional[str]