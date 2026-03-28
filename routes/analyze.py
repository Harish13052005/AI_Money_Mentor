from fastapi import APIRouter, HTTPException
from models.models import UserInput, FinancialPlan
from agents.orchestrator_agent import OrchestratorAgent
from services.openai_service import AIService
from services.llm_provider import LLMProviderManager, LLMProvider
from agents.explanation_agent import ExplanationAgent
from services.memory_service import SimpleMemory
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter()

# ============ Multi-Provider LLM Configuration ============
# Read API keys from environment variables
api_keys = {
    "groq": os.getenv("GROQ_API_KEY"),
    "openai": os.getenv("OPENAI_API_KEY"),
    "huggingface": os.getenv("HUGGINGFACE_API_KEY"),
    "together": os.getenv("TOGETHER_API_KEY"),
}

# Get primary provider from environment (defaults to groq for free tier)
primary_provider_name = os.getenv("AI_PROVIDER", "groq").lower()

# Initialize provider manager with fallback chain
try:
    provider_manager = LLMProviderManager(api_keys)
    
    # Try to set primary provider
    if primary_provider_name in [p.value for p in LLMProvider]:
        provider_enum = LLMProvider[primary_provider_name.upper()]
        if not provider_manager.set_provider(provider_enum):
            logger.warning(f"Primary provider {primary_provider_name} not available, using fallback chain")
    
    logger.info(f"Available LLM providers: {provider_manager.get_available_providers()}")
    logger.info(f"Provider health check: {provider_manager.health_check()}")
except Exception as e:
    logger.error(f"Failed to initialize provider manager: {e}")
    raise

# Initialize AI service with provider manager
ai_service = AIService(provider_manager)

# Initialize agents
orchestrator = OrchestratorAgent(ai_service)
explanation_agent = ExplanationAgent(ai_service)
memory = SimpleMemory()

@router.post("/analyze", response_model=FinancialPlan)
async def analyze_financial_data(data: UserInput):
    try:
        logger.info(f"Analyzing financial data for user with income: {data.income}")
        result_state = orchestrator.run_workflow(data.dict())

        if result_state.get("error"):
            logger.error(f"Workflow error: {result_state['error']}")
            raise HTTPException(status_code=400, detail=result_state["error"])

        final_output = result_state.get("final_output")
        if not final_output:
            raise HTTPException(status_code=500, detail="No output generated")

        # Store in memory for follow-up explanations
        memory.store("last_analysis", final_output.dict())
        logger.info("Analysis completed successfully")
        return final_output
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain")
async def explain(body: dict):
    try:
        question = body.get("question", "").strip()
        context = body.get("context", {})

        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        logger.info(f"Generating explanation for question: {question[:50]}...")
        
        last_analysis = memory.retrieve("last_analysis")
        if last_analysis:
            context = {**context, "previous_analysis": last_analysis}

        explanation = explanation_agent.explain(question, context)
        logger.info("Explanation generated successfully")
        return {"explanation": explanation}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error generating explanation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint for LLM providers.
    Returns status of all available providers and current configuration.
    """
    try:
        health_status = ai_service.health_check()
        available_providers = ai_service.get_available_providers()
        
        return {
            "status": "healthy" if any(health_status.values()) else "unhealthy",
            "available_providers": available_providers,
            "provider_health": health_status,
            "primary_provider": primary_provider_name,
            "total_providers": len(available_providers)
        }
    except Exception as e:
        logger.exception(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.post("/set-provider")
async def set_provider(body: dict):
    """
    Set the primary LLM provider.
    
    Request body:
    {
        "provider": "groq" | "openai" | "huggingface" | "together"
    }
    """
    try:
        provider_name = body.get("provider", "").lower()
        
        if not provider_name:
            raise HTTPException(status_code=400, detail="Provider name required")
        
        success = ai_service.set_provider(provider_name)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{provider_name}' not available. Available: {ai_service.get_available_providers()}"
            )
        
        return {
            "status": "success",
            "primary_provider": provider_name,
            "available_providers": ai_service.get_available_providers()
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error setting provider: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))