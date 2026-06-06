# 🚀 AI Money Mentor - Quick Start Guide

## ✅ What's Fixed

### 1. **Form Input Issues**
- ✓ Goal input now accepts empty input without breaking
- ✓ Investments list properly filtered to exclude empty entries
- ✓ Better default values for easier testing

### 2. **API Endpoint Fixes**
- ✓ `/explain` endpoint now accepts query parameters (not JSON body)
- ✓ Field validation with proper error messages
- ✓ Context parameter correctly handled

### 3. **UI Improvements**
- ✓ Beautiful, professional Streamlit interface with navigation
- ✓ Emoji icons for better visual hierarchy
- ✓ Organized sections with tabs for results
- ✓ Proper error messages and loading states
- ✓ Summary metrics display before analysis

## 🎯 How to Use

### 1. **Start the Backend Server**
```bash
.venv\Scripts\activate
python main.py
```
Server runs on: http://192.168.0.108:8000
API docs available at: http://192.168.0.108:8000/docs

### 2. **Start the Streamlit Frontend**
```bash
.venv\Scripts\activate
streamlit run app.py
```
- Frontend runs on: http://localhost:8501
- Choose section from sidebar: Financial Analysis, Ask for Explanation, or About

### 3. **Test via API**
```bash
# Using test script
python test_system.py

# Using curl (Windows)
test_api.bat

# Or using any HTTP client
POST http://192.168.0.108:8000/analyze
Content-Type: application/json

{
  "income": 5000,
  "expenses": 3000,
  "savings": 1000,
  "investments": [
    {"type": "stocks", "amount": 2000},
    {"type": "mutual_funds", "amount": 1000}
  ],
  "goals": ["buy house", "retirement"]
}
```

## 🎨 UI Sections

### **Financial Analysis Tab**
1. Enter your financial details (income, expenses, savings)
2. Add investments (type and amount)
3. Set your financial goals
4. View automatic calculations and metrics
5. Click "Generate Financial Plan"
6. Review results in 4 tabs: Summary, Issues, Plan, Actions

### **Ask for Explanation Tab**
1. Type your question about the analysis
2. Click "Get Explanation"
3. Receive AI-powered explanation
4. Read detailed reasoning for recommendations

### **About Tab**
- Learn about AI Money Mentor
- Understand how it works
- Get feature overview

## 🔧 Configuration

### Required: OpenAI API Key
1. Get key from: https://platform.openai.com/api-keys
2. Add to `.env` file:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

### Optional: Customize Port
Edit `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Change port here
```

## 📊 Example Workflow

### Input Example
```json
{
  "income": 5000,
  "expenses": 3000,
  "savings": 1000,
  "investments": [
    {"type": "stocks", "amount": 2000},
    {"type": "mutual_funds", "amount": 1000},
    {"type": "bonds", "amount": 500}
  ],
  "goals": ["Early retirement at 50", "Buy a rental property", "Kids education fund"]
}
```

### Output Example
```json
{
  "summary": "Savings rate: 40.0%, Risk: Medium",
  "issues": ["Insufficient emergency fund"],
  "financial_plan": "Build emergency fund to cover 6 months of expenses...",
  "recommended_actions": [
    "Allocate $1,809 monthly to emergency savings",
    "Consider diversifying stock holdings",
    "Review bond allocation quarterly"
  ],
  "risk_level": "Medium",
  "explanation": "Your current portfolio is well-diversified..."
}
```

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is in use: `netstat -ano | findstr :8000`
- Kill process: `taskkill /PID <PID> /F`
- Restart: `python main.py`

### Streamlit won't connect to backend
- Verify backend is running: Open http://192.168.0.39:8000/docs
- Check firewall settings
- Try with direct URL: http://192.168.0.39:8000

### OpenAI API errors
- Check API key is valid and in `.env` file
- Verify account has API credits
- Check API key from https://platform.openai.com/account/api-keys

### "Field required" error
- Ensure all required fields are filled:
  - Income > 0
  - Expenses ≥ 0
  - At least one goal
  - Valid investment types if adding investments

## 📝 Running Tests

```bash
# Test API endpoints
python test_system.py

# Run pytest tests
pytest

# Test specific module
pytest tests/test_models.py -v
```

## 🚢 Deployment

### Docker Deployment
```bash
docker-compose up --build
```
- Access at: http://192.168.0.39:8000

### Manual Deployment
1. Set up Python environment
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables
4. Run: `python main.py`
5. Access backend at: http://192.168.0.39:8000

## 📞 Support

- Check API docs: http://192.168.0.39:8000/docs
- Review logs: `app.log`
- Check error messages in Streamlit UI
- Verify environment configuration

## 🎓 Architecture

```
Request Flow:
Streamlit UI → FastAPI Backend → Orchestrator Agent
                                 ├── Data Intake Agent
                                 ├── Analysis Agent
                                 ├── Strategy Agent
                                 ├── Compliance Agent
                                 └── Action Agent
                ↓
            OpenAI API
```

---

**Version**: 1.0  
**Last Updated**: 2026-03-22