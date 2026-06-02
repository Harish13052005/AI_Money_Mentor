# AI Money Mentor – Agentic Financial Intelligence System

A multi-agent AI system for personalized financial planning.

## Features

- Multi-agent architecture with LangGraph orchestration
- Financial analysis and personalized planning
- Explainable AI responses
- Simple memory for previous analyses
- Logging and audit trail
- Web API and Streamlit frontend
- Docker deployment ready

## Setup

1. Clone the repository and navigate to the directory.

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set OpenAI API key in `.env`:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

4. Run the backend server:
   ```bash
   python main.py
   ```

5. (Optional) Run tests:
   ```bash
   pytest
   ```

## API Endpoints

- `POST /analyze`: Analyze financial data
- `POST /explain`: Get explanations for previous analysis

## Sample Input

```json
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

## Sample Output

```json
{
  "summary": "Savings rate: 40.0%, Risk: Medium",
  "issues": ["Insufficient emergency fund"],
  "financial_plan": "Build emergency fund, diversify investments...",
  "recommended_actions": ["Save more for emergency", "Invest in bonds"],
  "risk_level": "Medium",
  "explanation": "Plan generated based on your data and goals."
}
```

## Deployment

### Using Docker

1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Or manually:
   ```bash
   docker build -t ai-money-mentor .
   docker run -p 8000:8000 --env-file .env ai-money-mentor
   ```

### Local Development

- Backend: `python main.py`
- Frontend: `streamlit run app.py`

## Mobile App (Expo)

1. Change into the `mobile_app` folder and install dependencies:

```bash
cd mobile_app
npm install
```

2. Start the Expo development server:

```bash
npm run start
```

3. Update `mobile_app/services/api.js` `API_BASE` to point to your backend host:

- For Android emulator: `http://10.0.2.2:8000`
- For iOS simulator: `http://localhost:8000`
- For physical device: `http://<YOUR_MACHINE_IP>:8000`

4. Build a production app using Expo Application Services (EAS) or publish via the Expo Go app.

## Project Structure

```
ET_GenAI/
├── agents/                 # Agent implementations
├── services/               # OpenAI, memory, logging
├── routes/                 # FastAPI routes
├── models/                 # Pydantic models
├── main.py                 # FastAPI app
├── app.py                  # Streamlit frontend
├── requirements.txt        # Dependencies
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker compose
├── .env                    # Environment variables
└── README.md               # This file
```