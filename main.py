import os
import uvicorn
from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from services.llm_provider import LLMProviderManager
from services.openai_service import AIService
from database import SessionLocal, engine, get_db
from models import db_models
from schemas import UserCreate, User, Token, FinancialRecordResponse
from services.logging_config import LOGGING_CONFIG # Ensure logging is applied

logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI(title="AI Money Mentor API")

# Allow CORS for local development (adjust origins for production)
# React Native/Expo mobile apps typically do not enforce browser CORS,
# but this allows network calls from LAN devices during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
db_models.Base.metadata.create_all(bind=engine)


# Initialize Multi-Provider AI Service
api_keys = {
    "groq": os.getenv("GROQ_API_KEY"),
    "openai": os.getenv("OPENAI_API_KEY"),
    "together": os.getenv("TOGETHER_API_KEY"),
    "huggingface": os.getenv("HUGGINGFACE_API_KEY"),
}

provider_manager = LLMProviderManager(api_keys, primary_provider=os.getenv("AI_PROVIDER", "groq"))
ai_service = AIService(provider_manager)
from auth import (
    authenticate_user, create_access_token, get_password_hash,
    get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

class Investment(BaseModel):
    type: str
    amount: float

class AnalyzeRequest(BaseModel):
    income: float
    expenses: float
    savings: float
    investments: List[Investment]
    goals: List[str]

@app.post("/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(db_models.User).filter(db_models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = db.query(db_models.User).filter(db_models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = db_models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: db_models.User = Depends(get_current_active_user)):
    return current_user

@app.post("/analyze")
async def analyze_finance(
    data: AnalyzeRequest,
    current_user: db_models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        # Ensure investments are stored as JSON serializable
        investments_json = [inv.dict() for inv in data.investments]

        # Basic analysis logic
        savings_rate = ((data.income - data.expenses) / data.income) * 100 if data.income > 0 else 0
        issues = []
        if savings_rate < 20:
            issues.append("Low savings rate. Aim for at least 20%.")
        if data.savings < (data.expenses * 3):
            issues.append("Emergency fund is below recommended 3-6 months of expenses.")
        
        # Generate financial plan using AI service
        plan_content = ai_service.generate_strategy(
            {"savings_rate": round(savings_rate, 2), "risk_level": "Medium", "issues": issues},
            data.goals
        )

        analysis_context = {
            "savings_rate": round(savings_rate, 2),
            "risk_level": "Medium",
            "issues": issues
        }
        
        # Save financial record to database
        financial_record = db_models.FinancialRecord(
            user_id=current_user.id,
            income=data.income,
            expenses=data.expenses,
            savings=data.savings,
            investments=investments_json, # Store as JSON
            goals=data.goals, # Store as JSON
            analysis_result={
                "summary": f"Savings rate: {analysis_context['savings_rate']}%, Risk: Medium",
                "issues": issues,
                "financial_plan": plan_content,
                "recommended_actions": ["Increase emergency fund", "Diversify portfolio"], # Placeholder
                "risk_level": "Medium"
            },
            created_at=datetime.utcnow()
        )
        db.add(financial_record)
        db.commit()
        db.refresh(financial_record)
        
        return {
            "summary": f"Savings rate: {analysis_context['savings_rate']}%, Risk: Medium",
            "issues": issues,
            "financial_plan": plan_content,
            "recommended_actions": ["Increase emergency fund", "Diversify portfolio"],
            "risk_level": "Medium"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain")
async def get_explanation(question: str = Query(...), context: str = Query("")):
    explanation = ai_service.generate_explanation(question, {"additional_info": context})
    return {"explanation": explanation}

@app.get("/history", response_model=List[FinancialRecordResponse])
async def get_financial_history(
    current_user: db_models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return current_user.records


@app.get("/records/{record_id}", response_model=FinancialRecordResponse)
async def get_financial_record(record_id: int, current_user: db_models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    record = db.query(db_models.FinancialRecord).filter(db_models.FinancialRecord.id == record_id, db_models.FinancialRecord.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@app.put("/records/{record_id}", response_model=FinancialRecordResponse)
async def update_financial_record(record_id: int, data: AnalyzeRequest, current_user: db_models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    record = db.query(db_models.FinancialRecord).filter(db_models.FinancialRecord.id == record_id, db_models.FinancialRecord.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    try:
        record.income = data.income
        record.expenses = data.expenses
        record.savings = data.savings
        record.investments = [inv.dict() for inv in data.investments]
        record.goals = data.goals

        # Re-run analysis using existing simple logic + AI service
        savings_rate = ((data.income - data.expenses) / data.income) * 100 if data.income > 0 else 0
        issues = []
        if savings_rate < 20:
            issues.append("Low savings rate. Aim for at least 20%.")
        if data.savings < (data.expenses * 3):
            issues.append("Emergency fund is below recommended 3-6 months of expenses.")

        plan_content = ai_service.generate_strategy({"savings_rate": round(savings_rate, 2), "risk_level": "Medium", "issues": issues}, data.goals)

        record.analysis_result = {
            "summary": f"Savings rate: {round(savings_rate,2)}%, Risk: Medium",
            "issues": issues,
            "financial_plan": plan_content,
            "recommended_actions": ["Increase emergency fund", "Diversify portfolio"],
            "risk_level": "Medium"
        }

        db.add(record)
        db.commit()
        db.refresh(record)

        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    health = ai_service.health_check()
    return {"status": "online", "providers": health}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)