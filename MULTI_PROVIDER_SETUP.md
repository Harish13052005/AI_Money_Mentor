# 🔧 Multi-Provider LLM Setup Guide

## Overview

The AI Money Mentor system now supports **multiple LLM providers** to eliminate dependency on expensive APIs. This guide walks you through setting up FREE and freemium alternatives to OpenAI.

## Problem We Solved

**Before**: Single OpenAI dependency → 429 quota errors → Service down
**After**: Multiple providers with automatic fallback → Reliable, cost-free service

## Provider Comparison

| Provider | Cost | Speed | Rate Limit | Model Selection | Status |
|----------|------|-------|-----------|-----------------|--------|
| **Groq** | FREE | ⚡⚡⚡ Fastest | 30 req/min | Limited (4 models) | 🟢 RECOMMENDED |
| **Together AI** | FREE ($5/mo) | ⚡⚡ Fast | Generous | Large selection | 🟢 EXCELLENT |
| **HuggingFace** | FREE | ⚡ Moderate | Rate limited | Huge selection | 🟡 GOOD |
| **OpenAI** | PAID ($) | ⚡⚡ Fast | Quota based | All models | 🔴 FALLBACK ONLY |

## Step-by-Step Setup

### 1️⃣ Install Dependencies for Multi-Provider Support

```bash
# Essential for Groq (recommended)
pip install groq

# Optional for other providers
pip install together          # For Together AI
pip install huggingface-hub   # For HuggingFace
pip install openai            # For OpenAI fallback
```

### 2️⃣ Setup Groq (Recommended - FREE)

**Why Groq?**
- Completely FREE with no usage limits
- Fastest inference speeds (industry leading)
- 30 requests per minute (sufficient for most applications)
- Simple integration

**Steps:**
1. Go to https://console.groq.com
2. Sign up (free account)
3. Create an API key
4. Add to `.env`:
   ```
   GROQ_API_KEY=gsk_your_api_key_here
   AI_PROVIDER=groq
   ```

**Available Models:**
- `mixtral-8x7b-32768` (Best balance of speed/quality)
- `llama2-70b-4096`
- `gemma-7b-it`

### 3️⃣ Setup Together AI (FREE - $5/mo credits)

**Why Together AI?**
- Free tier with $5 monthly credits
- Large selection of open-source models
- Good fallback option

**Steps:**
1. Go to https://www.together.ai
2. Sign up (free)
3. Get API key from dashboard
4. Add to `.env`:
   ```
   TOGETHER_API_KEY=your_together_api_key
   ```

**Available Models:**
- mistralai/Mistral-7B-Instruct-v0.1
- mistralai/Mistral-7B-Instruct-v0.2
- meta-llama/llama-2-7b-chat-hf
- And many more...

### 4️⃣ Setup HuggingFace (FREE)

**Why HuggingFace?**
- Free inference API
- Largest model library
- Third-level fallback

**Steps:**
1. Go to https://huggingface.co
2. Sign up (free)
3. Create access token at Settings → Access Tokens
4. Add to `.env`:
   ```
   HUGGINGFACE_API_KEY=hf_your_access_token
   ```

### 5️⃣ OpenAI Setup (Optional - FALLBACK ONLY)

Only use if you have active OpenAI quota:

```
OPENAI_API_KEY=sk_test_your_key_here
```

## Configuration

### .env File

```bash
# Primary provider (defaults to groq)
AI_PROVIDER=groq

# API Keys (set at least Groq)
GROQ_API_KEY=gsk_...
TOGETHER_API_KEY=key_...
HUGGINGFACE_API_KEY=hf_...
OPENAI_API_KEY=sk_...  # Optional
```

### Fallback Chain (Automatic)

If configured provider fails:
1. Groq
2. Together AI
3. HuggingFace
4. OpenAI

The system **automatically switches** to the next available provider.

## Available API Endpoints

### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "available_providers": ["groq", "together", "huggingface"],
  "provider_health": {
    "groq": true,
    "together": true,
    "huggingface": false,
    "openai": false
  },
  "primary_provider": "groq",
  "total_providers": 3
}
```

### Change Provider at Runtime
```bash
POST /set-provider

Body: {"provider": "together"}

Response:
{
  "status": "success",
  "primary_provider": "together",
  "available_providers": ["groq", "together", "huggingface"]
}
```

### Analyze Financial Data
```bash
POST /analyze
# Now uses multi-provider system automatically
```

### Get Explanation
```bash
POST /explain
# Falls back automatically if primary provider fails
```

## Testing Your Setup

### 1. Check Provider Health
```bash
curl http://localhost:8000/health
```

### 2. Test Analysis
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "income": 5000,
    "expenses": 3000,
    "goals": {"emergency": 1000},
    "risk_preference": "moderate"
  }'
```

### 3. View Logs
The system logs which provider is being used:
```
INFO: Available LLM providers: ['groq', 'together', 'huggingface']
INFO: Using groq provider
INFO: Successfully used groq provider
```

## Troubleshooting

### Problem: "All LLM providers failed"
**Solution:** 
- Check internet connection
- Verify API keys in `.env`
- Check provider quota/rate limits
- Run `curl http://localhost:8000/health`

### Problem: Provider timeout
**Solution:**
- Check your internet connection
- Try switching to different provider with `/set-provider`
- Reduce max_tokens in prompts

### Problem: HuggingFace says model is loading
**Solution:**
- HuggingFace models may need to be loaded first
- Wait a minute for model to initialize
- Switch to Groq (instant response)

### Problem: Rate limit exceeded
**Solution:**
```python
# Check current provider limits in response headers
# Automatically falls back to next provider
# Consider upgrading to paid tier
```

## Cost Analysis

### Monthly Cost (Estimated)

**Scenario: 1000 API calls/month per endpoint**

| Provider | Cost | Notes |
|----------|------|-------|
| Groq | $0 | 100% FREE |
| Together | $0 | FREE ($5 credit) |
| HuggingFace | $0 | FREE (rate limited) |
| Together (paid) | $5-20 | If you exceed free tier |
| OpenAI (gpt-3.5) | $50-100 | Expensive! |

**With this setup: $0 - $5/month** (vs $50-100 with OpenAI only)

## Production Recommendations

1. **Use Groq as primary** (fastest, free, no quota)
2. **Configure Together AI as fallback** (generous free tier)
3. **Add HuggingFace as tertiary** (last resort)
4. **Keep OpenAI configured** (emergency fallback)
5. **Monitor health endpoint** regularly
6. **Setup alerts** if all providers go down

## Code Examples

### Checking Available Providers

```python
from routes.analyze import ai_service

# Get available providers
providers = ai_service.get_available_providers()
print(f"Available: {providers}")

# Check health
health = ai_service.health_check()
print(f"Health: {health}")

# Set primary provider
ai_service.set_provider("together")
```

### Custom Provider Configuration

```python
from services.llm_provider import LLMProviderManager

api_keys = {
    "groq": "gsk_...",
    "together": "key_...",
    "huggingface": "hf_...",
    "openai": "sk_...",
}

manager = LLMProviderManager(api_keys)
text = manager.generate_text("Your prompt here")
```

## Migration from OpenAI-Only

### Old Code:
```python
from services.openai_service import OpenAIService

service = OpenAIService(api_key="sk_...")
```

### New Code:
```python
from services.llm_provider import LLMProviderManager
from services.openai_service import AIService

manager = LLMProviderManager(api_keys)
service = AIService(manager)
```

## Additional Resources

- **Groq Docs**: https://console.groq.com/docs
- **Together AI Docs**: https://together.ai/docs
- **HuggingFace Docs**: https://huggingface.co/docs/api-inference
- **OpenAI Docs**: https://platform.openai.com/docs

## Support

If you encounter issues:
1. Check logs in `/logs/`
2. Run health check: `curl http://localhost:8000/health`
3. Verify `.env` configuration
4. Check provider status pages

---

**Version**: 1.0 | **Last Updated**: March 2026 | **Status**: Production Ready ✅
