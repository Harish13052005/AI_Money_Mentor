from models.models import AnalysisResult

class ComplianceSafetyAgent:
    def check(self, analysis: AnalysisResult, strategy: str) -> bool:
        # Simple checks
        if analysis.risk_level == "High" and "high risk" in strategy.lower():
            # If high risk and strategy suggests high risk, maybe flag, but for now pass
            pass
        # Prevent unrealistic advice, e.g., if low savings, don't recommend aggressive investing
        if analysis.savings_rate < 10 and "invest heavily" in strategy.lower():
            return False
        return True