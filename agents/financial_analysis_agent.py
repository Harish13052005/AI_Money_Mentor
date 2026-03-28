from models.models import UserInput, AnalysisResult
from typing import List

class FinancialAnalysisAgent:
    def analyze(self, user_input: UserInput) -> AnalysisResult:
        savings_rate = ((user_input.income - user_input.expenses) / user_input.income) * 100 if user_input.income > 0 else 0
        issues = self.detect_issues(user_input, savings_rate)
        risk_level = self.estimate_risk(user_input)
        return AnalysisResult(
            savings_rate=round(savings_rate, 2),
            risk_level=risk_level,
            issues=issues
        )

    def detect_issues(self, user_input: UserInput, savings_rate: float) -> List[str]:
        issues = []
        # No emergency fund: assume 3 months expenses
        emergency_fund_needed = user_input.expenses * 3
        if user_input.savings < emergency_fund_needed:
            issues.append("Insufficient emergency fund")
        # Low savings rate
        if savings_rate < 20:
            issues.append("Low savings rate")
        # Overexposure
        total_investments = sum(inv.amount for inv in user_input.investments)
        if total_investments > 0:
            for inv in user_input.investments:
                if (inv.amount / total_investments) > 0.7:
                    issues.append(f"Overexposure to {inv.type}")
        return issues

    def estimate_risk(self, user_input: UserInput) -> str:
        # Simple risk estimation based on investments
        stock_amount = sum(inv.amount for inv in user_input.investments if inv.type.lower() == "stocks")
        total_inv = sum(inv.amount for inv in user_input.investments)
        if total_inv == 0:
            return "Low"
        stock_ratio = stock_amount / total_inv
        if stock_ratio > 0.7:
            return "High"
        elif stock_ratio > 0.3:
            return "Medium"
        else:
            return "Low"