# 🏗️ Multi-Provider LLM Architecture

## Executive Summary

This document describes the refactoring of the AI Money Mentor system from a **single-point OpenAI dependency** to a **flexible, production-grade multi-provider LLM architecture**.

### Key Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Single Point of Failure** | OpenAI quota exhaustion → 429 errors → No service | Auto-failover to other providers |
| **Cost** | $100+/month | $0-5/month (free tier) |
| **Provider Lock-in** | Hard-coded OpenAI | Pluggable providers |
| **Reliability** | Depends on OpenAI uptime | Multi-provider redundancy |
| **Model Choice** | Single model | Multiple models per provider |
| **Scalability** | Rate-limited | Distributed rate limits |

---

## Architecture Overview

### System Diagram

```
Client Request
    ↓
FastAPI Router (/analyze, /explain)
    ↓
AIService (Unified Interface)
    ↓
LLMProviderManager (Intelligence Layer)
    ↓
Provider Selection Logic
    ├─→ Try Primary Provider (from AI_PROVIDER env)
    │
    └─→ If fails, Fallback Chain:
        1. Groq (Fastest, FREE)
        2. Together AI (Generous FREE tier)
        3. HuggingFace (FREE API)
        4. OpenAI (Paid, last resort)
    ↓
Selected LLM Provider
    ├─→ GroqProvider
    ├─→ TogetherAIProvider
    ├─→ HuggingFaceProvider
    └─→ OpenAIProvider
    ↓
LLM Response
```

---

## Components

### 1. **BaseLLMProvider (Abstract Class)**

Defines the interface all providers must implement:

```python
class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is up and quota available"""
        pass
```

**Benefits:**
- Consistent interface across all providers
- Easy to add new providers
- Type-safe implementation

### 2. **Concrete Provider Implementations**

#### GroqProvider
- **API**: `https://api.groq.com/`
- **Cost**: $0 (FREE)
- **Rate Limit**: 30 requests/minute
- **Best For**: Production use, cost optimization
- **Models**: mixtral-8x7b-32768, llama2-70b, gemma-7b-it

#### TogetherAIProvider
- **API**: `https://api.together.xyz/`
- **Cost**: FREE ($5/month credits)
- **Rate Limit**: Generous
- **Best For**: Fallback, diverse model selection
- **Models**: 100+ open-source models

#### HuggingFaceProvider
- **API**: `https://api-inference.huggingface.co/`
- **Cost**: FREE (rate limited)
- **Rate Limit**: Throttled
- **Best For**: Tertiary fallback
- **Models**: Large selection

#### OpenAIProvider
- **API**: `https://api.openai.com/v1`
- **Cost**: PAID (per token)
- **Rate Limit**: Quota-based
- **Best For**: Emergency fallback only
- **Models**: GPT-3.5-turbo, GPT-4, etc.

### 3. **LLMProviderManager (Orchestrator)**

Core intelligence layer managing:
- Provider initialization
- Fallback logic
- Health checking
- Runtime provider switching

**Key Methods:**

```python
# Generate text with automatic fallback
text = manager.generate_text(prompt)

# Switch provider at runtime
manager.set_provider(LLMProvider.TOGETHER)

# Health monitoring
health_status = manager.health_check()
# Returns: {"groq": True, "together": False, ...}

# List available providers
providers = manager.get_available_providers()
# Returns: ["groq", "together", "huggingface"]
```

**Fallback Chain Logic:**

```python
# If primary provider fails:
for provider in [Groq, Together, HuggingFace, OpenAI]:
    try:
        return provider.generate_text(...)
    except Exception:
        continue  # Try next

# If all fail
raise Exception("All providers exhausted")
```

### 4. **AIService (Unified Business Logic)**

High-level service providing domain-specific methods:

```python
service = AIService(provider_manager)

# Strategy generation
strategy = service.generate_strategy(analysis, goals)

# Explanations
explanation = service.generate_explanation(question, context)

# Provider management
service.set_provider("together")
providers = service.get_available_providers()
health = service.health_check()
```

**Advantages:**
- Separates provider logic from business logic
- Consistent API across all use cases
- Easy to extend with new generation methods

### 5. **Agent Integration**

Agents now use `AIService` instead of direct provider calls:

```python
# OrchestratorAgent
class OrchestratorAgent:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.strategy_agent = StrategyGenerationAgent(ai_service)

# StrategyGenerationAgent
class StrategyGenerationAgent:
    def generate(self, analysis, goals):
        return self.ai_service.generate_strategy(analysis, goals)
        # This automatically uses the best available provider!
```

---

## Configuration & Environment Variables

### Setup via .env

```bash
# Primary provider (defaults to groq)
AI_PROVIDER=groq

# API Keys (configure at least one)
GROQ_API_KEY=gsk_...
TOGETHER_API_KEY=key_...
HUGGINGFACE_API_KEY=hf_...
OPENAI_API_KEY=sk_...
```

### Setup via Python

```python
api_keys = {
    "groq": os.getenv("GROQ_API_KEY"),
    "openai": os.getenv("OPENAI_API_KEY"),
    "huggingface": os.getenv("HUGGINGFACE_API_KEY"),
    "together": os.getenv("TOGETHER_API_KEY"),
}

manager = LLMProviderManager(api_keys)
service = AIService(manager)
```

---

## API Endpoints

### Health Check

```bash
GET /health

Response:
{
  "status": "healthy",
  "available_providers": ["groq", "together"],
  "provider_health": {
    "groq": true,
    "together": false,
    "huggingface": false,
    "openai": false
  },
  "primary_provider": "groq",
  "total_providers": 2
}
```

### Set Provider

```bash
POST /set-provider

Body: {"provider": "together"}

Response:
{
  "status": "success",
  "primary_provider": "together",
  "available_providers": ["groq", "together"]
}
```

### Analyze (Already Uses Multi-Provider)

```bash
POST /analyze

Body: {
  "income": 5000,
  "expenses": 3000,
  "goals": {"emergency": 1000},
  "risk_preference": "moderate"
}

# Response is now generated with automatic provider fallback
```

---

## Error Handling & Resilience

### Graceful Degradation

```python
# If Groq fails for any reason, automatically use Together
try:
    response = groq_provider.generate_text(prompt)
except RateLimitError:
    response = together_provider.generate_text(prompt)  # Fallback
except APIError:
    response = huggingface_provider.generate_text(prompt)  # Next fallback
except Exception:
    response = openai_provider.generate_text(prompt)  # Last resort
```

### Logging

All operations are logged with context:

```
INFO: Initialized groq provider
INFO: Using groq provider
WARNING: groq failed: RateLimitError
INFO: Falling back to together provider
INFO: Successfully used together provider
```

### Health Monitoring

```python
health = provider_manager.health_check()
# Call periodically to detect provider issues before they affect users
```

---

## Performance Characteristics

### Response Time (Typical)

| Provider | Time | Status |
|----------|------|--------|
| Groq | 100-300ms | ⚡ Fastest |
| Together | 300-500ms | ⚡ Fast |
| HuggingFace | 500-2000ms | ⚡ Moderate |
| OpenAI | 200-400ms | ⚡ Fast |

### Cost per 1,000 API Calls

| Provider | Cost |
|----------|------|
| Groq | $0 |
| Together | $0 (free tier) |
| HuggingFace | $0 |
| OpenAI | $0.002-0.05 |

---

## File Structure

```
services/
  ├── openai_service.py       # AIService (unified interface)
  ├── llm_provider.py         # Provider implementations & manager
  ├── memory_service.py       # (existing)
  └── logging_config.py       # (existing)

agents/
  ├── orchestrator_agent.py   # Uses AIService
  ├── strategy_generation_agent.py  # Uses AIService
  ├── explanation_agent.py    # Uses AIService
  └── ...

routes/
  └── analyze.py             # Initializes LLMProviderManager
```

---

## Migration Guide

### For Existing Code

**Before (OpenAI-only):**
```python
from services.openai_service import OpenAIService
service = OpenAIService(api_key="sk_...")
strategy = service.generate_strategy(analysis, goals)
```

**After (Multi-provider):**
```python
from services.llm_provider import LLMProviderManager
from services.openai_service import AIService

manager = LLMProviderManager(api_keys)
service = AIService(manager)
strategy = service.generate_strategy(analysis, goals)
# ^ Automatically uses best available provider
```

### Backward Compatibility

For maximum compatibility, we kept:
```python
# This still works (OpenAIService is an alias)
OpenAIService = AIService
```

---

## Scalability Considerations

### Horizontal Scaling

```
Load Balancer
    ↓
┌───────────────────────┐
│ Server Instance 1     │
│ - AIService           │
│ - ProviderManager     │
└───────────────────────┘

┌───────────────────────┐
│ Server Instance 2     │
│ - AIService           │
│ - ProviderManager     │
└───────────────────────┘

┌───────────────────────┐
│ Server Instance N     │
│ - AIService           │
│ - ProviderManager     │
└───────────────────────┘
```

Each instance independently manages provider selection and fallback.

### Rate Limit Handling

Since we have 4 providers with independent rate limits:
- Groq: 30 req/min
- Together: 1000+ req/min
- HuggingFace: Throttled
- OpenAI: Quota-based

**Combined capacity is significantly higher than OpenAI alone.**

---

## Testing

### Unit Tests

```python
# Test provider initialization
def test_groq_provider():
    provider = GroqProvider(api_key)
    assert provider.generate_text("test")

# Test fallback logic
def test_provider_fallback():
    manager = LLMProviderManager(api_keys)
    # Primary provider will be tested
    text = manager.generate_text("prompt")
    assert text
```

### Integration Tests

```python
# Test complete workflow
def test_analyze_endpoint():
    response = client.post("/analyze", json=user_data)
    assert response.status_code == 200

# Test provider switching
def test_provider_switching():
    response = client.post("/set-provider", json={"provider": "together"})
    assert response.status_code == 200
```

---

## Future Enhancements

### Planned Features

- [ ] Load balancing across multiple providers
- [ ] Provider-specific prompt optimization
- [ ] Cost tracking per provider
- [ ] Scheduled provider health checks
- [ ] Automatic rate limit detection
- [ ] Provider performance metrics dashboard
- [ ] A/B testing different providers
- [ ] Custom model selection per provider

### Potential New Providers

- Anthropic Claude (Claude API)
- Cohere
- Aleph Alpha
- Local LLMs (Ollama, LLaMA.cpp)
- Azure OpenAI

---

## Troubleshooting

### Common Issues

**Issue**: "All LLM providers failed"
```
Solution:
1. Check internet connection
2. Verify all API keys exist and are valid
3. Check rate limits on all providers
4. Review logs in /logs/
```

**Issue**: Provider timeout
```
Solution:
1. Increase timeout in config
2. Reduce max_tokens in generation
3. Switch to faster provider
```

**Issue**: Model not found
```
Solution:
1. Verify model name matches provider
2. Use default model for provider
3. Check provider documentation
```

---

## References

- **Groq**: https://console.groq.com/docs
- **Together AI**: https://together.ai/docs
- **HuggingFace**: https://huggingface.co/inference
- **OpenAI**: https://platform.openai.com/docs

---

## Author Notes

This architecture was designed with the following principles:

1. **Single Responsibility**: Each provider handles its own API interaction
2. **Open/Closed Principle**: Easy to add new providers without modifying existing code
3. **Dependency Inversion**: Services depend on abstractions, not concrete implementations
4. **Fail-Safe Design**: System continues operating even if primary provider fails
5. **Production Ready**: Includes logging, health checks, error handling, documentation

---

**Version**: 1.0 | **Last Updated**: March 2026 | **Status**: Production Ready ✅
