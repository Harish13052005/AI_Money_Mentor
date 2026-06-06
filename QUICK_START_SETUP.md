# ⚡ Quick Start: Multi-Provider LLM Setup

## 30-Second Setup (Fastest Path)

### 1. Get Groq API Key (FREE)
```bash
# Visit: https://console.groq.com
# Create account → Create API key → Copy it
```

### 2. Create .env File
```bash
# In project root, create .env:
echo "GROQ_API_KEY=gsk_your_key_here" > .env
echo "AI_PROVIDER=groq" >> .env
```

### 3. Install & Run
```bash
pip install -r requirements.txt
# Terminal 1: Backend
python main.py

# Terminal 2: Frontend
streamlit run app.py
```

✅ **Done!** System running on `http://localhost:8501`

---

## 2-Minute Setup (Production Ready)

### 1. Interactive Setup Script
```bash
python setup_llm_providers.py
# Follow the prompts to configure providers
```

### 2. Verify Configuration
```bash
# Check health endpoint
curl http://192.168.0.108:8000/health

# Expected output:
# {
#   "status": "healthy",
#   "available_providers": ["groq"],
#   "total_providers": 1
# }
```

### 3. Run System
```bash
# Backend
python main.py

# Frontend (new terminal)
streamlit run app.py
```

---

## Provider Ranking (Choose 1-3)

### 🏆 Tier 1: MUST HAVE (Groq)
- **Cost**: FREE
- **Speed**: Fastest
- **Reliability**: Excellent
- **Setup time**: 2 minutes
- **Link**: https://console.groq.com

### 🥈 Tier 2: Should Have (Together AI)
- **Cost**: FREE ($5/month credits)
- **Speed**: Fast
- **Reliability**: Very Good
- **Setup time**: 3 minutes
- **Link**: https://www.together.ai

### 🥉 Tier 3: Nice to Have (HuggingFace)
- **Cost**: FREE (rate limited)
- **Speed**: Moderate
- **Reliability**: Good
- **Setup time**: 2 minutes
- **Link**: https://huggingface.co

### ❌ Avoid: OpenAI (Keep as Fallback Only)
- **Cost**: $50+ per month
- **When to use**: Only if Groq fails
- **Setup time**: 5 minutes (if needed)

---

## Configuration Examples

### Minimum (Works!)
```bash
# .env
GROQ_API_KEY=gsk_your_key
AI_PROVIDER=groq
```

### Recommended (Production)
```bash
# .env
GROQ_API_KEY=gsk_groq_key
TOGETHER_API_KEY=together_key
HUGGINGFACE_API_KEY=hf_key
AI_PROVIDER=groq
```

### Maximum (Extra Safety)
```bash
# .env
GROQ_API_KEY=gsk_groq_key
TOGETHER_API_KEY=together_key
HUGGINGFACE_API_KEY=hf_key
OPENAI_API_KEY=sk_openai_key  # Last resort
AI_PROVIDER=groq
```

---

## Testing Your Setup

### Test 1: Check Health
```bash
curl http://192.168.0.108:8000/health
```

Expected: ✅ 200 OK with provider list

### Test 2: Check Logs
```bash
# Look for these success messages:
# "Initialized groq provider"
# "Successfully used groq provider"
```

### Test 3: Make API Call
```bash
curl -X POST http://192.168.0.108:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "income": 5000,
    "expenses": 3000,
    "goals": ["save_emergency_fund"],
    "risk_preference": "moderate"
  }'
```

Expected: ✅ 200 OK with financial plan

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "GROQ_API_KEY not configured" | Add to `.env`: `GROQ_API_KEY=your_key` |
| "All providers failed" | Check `.env`, internet, API keys |
| Timeout error | Groq might be slow, try fallback provider |
| 429 Rate limit | Groq has 30 req/min - space requests out |
| Model not found | Check provider docs for valid model names |

---

## Need Help?

1. **Documentation**: Read [MULTI_PROVIDER_SETUP.md](MULTI_PROVIDER_SETUP.md)
2. **Architecture**: Read [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Error Logs**: Check console output after running `python main.py`
4. **Health Check**: Run `curl http://192.168.0.39:8000/health`

---

## What Changed?

### Before (Old System):
- ❌ Single OpenAI dependency
- ❌ 429 quota errors crash everything
- ❌ Expensive ($50+/month)
- ❌ No fallback

### After (New System):
- ✅ Multiple free providers
- ✅ Auto-fallback if primary fails
- ✅ Cost: $0-5/month
- ✅ Production-grade reliability

---

## Environment Variable Reference

```bash
# PRIMARY PROVIDER (groq|together|huggingface|openai)
AI_PROVIDER=groq

# API KEYS (get these from provider websites)
GROQ_API_KEY=                    # https://console.groq.com
TOGETHER_API_KEY=                # https://www.together.ai
HUGGINGFACE_API_KEY=             # https://huggingface.co
OPENAI_API_KEY=                  # https://platform.openai.com
```

---

## One-Command Setup

```bash
# Install all dependencies
pip install -r requirements.txt

# Run interactive setup
python setup_llm_providers.py

# Start backend (terminal 1)
python main.py

# Start frontend (terminal 2)
streamlit run app.py
```

---

## Next Steps

1. ✅ Get API key from Groq (2 min)
2. ✅ Add to `.env` file (1 min)
3. ✅ Run `pip install -r requirements.txt` (2 min)
4. ✅ Start system (1 min)
5. ✅ Check health endpoint (1 min)
6. ✅ Test API (1 min)

**Total: ~8 minutes to production-ready system!**

---

## FAQ

**Q: Do I need an API key for all providers?**
A: No. Start with Groq (recommended). Add others for redundancy.

**Q: Which provider is fastest?**
A: Groq (100-300ms typical response time)

**Q: What if my Groq quota runs out?**
A: System automatically switches to Together AI → HuggingFace → OpenAI

**Q: Can I change providers at runtime?**
A: Yes! Call `POST /set-provider` with new provider name

**Q: Is my data sent to multiple providers?**
A: No. Only the primary provider (or fallback if primary fails) gets your request.

**Q: What's the cost?**
A: $0 with Groq. Literally free. No usage limits.

---

**Version**: 1.0 | Status: Ready to Use ✅
