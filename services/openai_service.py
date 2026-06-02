"""
Unified AI Service with multi-provider support.
Replaces direct OpenAI dependency with flexible provider abstraction.
"""
from typing import List, Dict, Optional
from services.llm_provider import LLMProviderManager, LLMProvider
import logging

logger = logging.getLogger(__name__)


class AIService:
    """
    Unified AI Service supporting multiple LLM providers.
    Handles strategy generation, explanations, and other AI tasks.
    """
    
    def __init__(self, provider_manager: LLMProviderManager, api_key: str = None):
        """
        Initialize AI Service.
        
        Args:
            provider_manager: LLMProviderManager instance
            api_key: Deprecated - kept for backward compatibility
        """
        self.provider_manager = provider_manager
        logger.info(f"AIService initialized with providers: {provider_manager.get_available_providers()}")
    
    def generate_strategy(self, analysis: dict, goals: List[str]) -> str:
        """
        Generate a personalized financial strategy.
        
        Args:
            analysis: Financial analysis results
            goals: User's financial goals
        
        Returns:
            Strategy text
        """
        prompt = f"""
You are a senior financial advisor. Based on the following financial analysis:

Savings Rate: {analysis['savings_rate']}%
Risk Level: {analysis['risk_level']}
Issues: {', '.join(analysis['issues'])}
Goals: {', '.join(goals)}

Generate a personalized, actionable financial plan with specific steps and timeline.
Keep the explanation concise but comprehensive.
"""
        try:
            return self.provider_manager.generate_text(
                prompt,
                max_tokens=500,
                temperature=0.7
            )
        except Exception as e:
            logger.error(f"Strategy generation failed: {e}")
            # Fallback for development/testing when all providers fail
            return f"""
Financial Strategy Plan (Development Fallback)

Based on your analysis:
- Savings Rate: {analysis['savings_rate']}%
- Risk Level: {analysis['risk_level']}
- Issues: {', '.join(analysis['issues']) if analysis.get('issues') else 'None identified'}

Recommended Goals:
{chr(10).join(f"- {goal}" for goal in goals)}

Action Plan:
1. Increase emergency fund to 3-6 months of expenses
2. Optimize spending habits based on current expenses
3. Diversify investments across asset classes
4. Review and rebalance portfolio quarterly
5. Automate savings and investment contributions

Timeline: Execute over 12 months for sustainable results.
Note: This is a development response. Connect valid AI providers for full personalized planning.
"""
    
    def generate_explanation(self, question: str, context: dict) -> str:
        """
        Generate an explanation for a financial question.
        
        Args:
            question: User's question
            context: Contextual information
        
        Returns:
            Explanation text
        """
        context_str = ""
        if isinstance(context, dict):
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
        elif isinstance(context, str) and context:
            context_str = context
        
        prompt = f"""You are a helpful financial advisor answering a user's question.

User Question: {question}

{"Context Information:" + context_str if context_str else ""}

Provide a clear, concise, and accurate explanation that directly answers the question.
"""
        try:
            return self.provider_manager.generate_text(
                prompt,
                max_tokens=400,
                temperature=0.7
            )
        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
            # Fallback for development/testing when all providers fail
            return f"""
Financial Explanation (Development Fallback)

Question: {question}

Explanation:
This is a development response providing general financial guidance. For personalized advice tailored to your specific situation, please ensure AI providers are properly configured with valid API keys.

Key Considerations:
- Review your financial goals and timeline
- Consider your risk tolerance and investment horizon
- Diversify investments across asset classes
- Maintain an emergency fund (3-6 months of expenses)
- Automate savings and investment contributions
- Rebalance portfolio regularly

For more detailed information, connect to a live AI provider.
"""
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return self.provider_manager.get_available_providers()
    
    def set_provider(self, provider_name: str) -> bool:
        """Set the primary provider to use."""
        try:
            provider = LLMProvider[provider_name.upper()]
            return self.provider_manager.set_provider(provider)
        except KeyError:
            logger.error(f"Unknown provider: {provider_name}")
            return False
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all providers."""
        return self.provider_manager.health_check()


# Backward compatibility alias
OpenAIService = AIService