from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class FinancialRecordResponse(BaseModel):
    id: int
    income: float
    expenses: float
    savings: float
    created_at: datetime
    analysis_result: Optional[dict] = None
    # Add other fields as needed for display

    class Config:
        from_attributes = True