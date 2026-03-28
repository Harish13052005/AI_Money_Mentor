from pydantic import BaseModel
from typing import List, Optional, TypedDict

class Investment(BaseModel):
    type: str
    amount: float

class UserInput(BaseModel):
    income: float
    expenses: float
    savings: float
    investments: List[Investment]
    goals: List[str]

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