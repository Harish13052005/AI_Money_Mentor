from services.openai_service import AIService

class ExplanationAgent:
    def __init__(self, ai_service: AIService):
        """Initialize with multi-provider AI service."""
        self.ai_service = ai_service

    def explain(self, question: str, context: dict) -> str:
        """Generate explanation using available LLM provider."""
        return self.ai_service.generate_explanation(question, context)