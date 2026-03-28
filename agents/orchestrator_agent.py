from models.models import UserInput, AnalysisResult, FinancialPlan
from agents.data_intake_agent import DataIntakeAgent
from agents.financial_analysis_agent import FinancialAnalysisAgent
from agents.strategy_generation_agent import StrategyGenerationAgent
from agents.compliance_safety_agent import ComplianceSafetyAgent
from agents.action_recommendation_agent import ActionRecommendationAgent
from services.openai_service import AIService
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)

class OrchestratorAgent:
    def __init__(self, ai_service: AIService):
        """Initialize orchestrator with AI service (supports multiple LLM providers)."""
        self.ai_service = ai_service
        self.data_agent = DataIntakeAgent()
        self.analysis_agent = FinancialAnalysisAgent()
        self.strategy_agent = StrategyGenerationAgent(ai_service)
        self.compliance_agent = ComplianceSafetyAgent()
        self.action_agent = ActionRecommendationAgent()

    def run_workflow(self, initial_data: dict) -> Dict[str, Any]:
        state: Dict[str, Any] = {
            "user_input": None,
            "analysis": None,
            "strategy": None,
            "compliance_check": None,
            "actions": None,
            "final_output": None,
            "error": None,
        }

        try:
            state["user_input"] = self.data_agent.process(initial_data)
            logging.info("Data intake completed")

            state["analysis"] = self.analysis_agent.analyze(state["user_input"])  # type: ignore
            logging.info("Analysis completed")

            state["strategy"] = self.strategy_agent.generate(state["analysis"], state["user_input"].goals)  # type: ignore
            logging.info("Strategy generated")

            state["compliance_check"] = self.compliance_agent.check(state["analysis"], state["strategy"])
            if not state["compliance_check"]:
                raise ValueError("Compliance check failed: Strategy may be unsafe")
            logging.info("Compliance checked")

            state["actions"] = self.action_agent.recommend(state["strategy"])
            state["final_output"] = FinancialPlan(
                summary=f"Savings rate: {state['analysis'].savings_rate}%, Risk: {state['analysis'].risk_level}",
                issues=state["analysis"].issues,
                financial_plan=state["strategy"],
                recommended_actions=state["actions"],
                risk_level=state["analysis"].risk_level,
                explanation="Plan generated based on your data and goals.",
            )
            logging.info("Actions recommended")

            return state

        except Exception as e:
            state["error"] = str(e)
            logging.error(f"Workflow error: {state['error']}")
            return state