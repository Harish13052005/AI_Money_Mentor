from models.models import AnalysisResult
from services.openai_service import AIService
from typing import List

class StrategyGenerationAgent:
    def __init__(self, ai_service: AIService):
        """Initialize with multi-provider AI service."""
        self.ai_service = ai_service

    def generate(self, analysis: AnalysisResult, goals: List[str]) -> str:
        """Generate financial strategy using available LLM provider."""
        analysis_dict = {
            "savings_rate": analysis.savings_rate,
            "risk_level": analysis.risk_level,
            "issues": analysis.issues
        }
        return self.ai_service.generate_strategy(analysis_dict, goals)