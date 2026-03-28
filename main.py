from fastapi import FastAPI
from routes.analyze import router as analyze_router
from services.logging_config import LOGGING_CONFIG
import logging.config

logging.config.dictConfig(LOGGING_CONFIG)

app = FastAPI(title="AI Money Mentor", description="Agentic Financial Intelligence System")

app.include_router(analyze_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)