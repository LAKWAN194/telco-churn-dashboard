from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.config import settings
from backend.routers import customers, predict, stats
from backend.services.db import get_db

app = FastAPI(
    title="Telco Churn API",
    description="Serves churn predictions and the numbers behind the dashboard.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(customers.router)
app.include_router(stats.router)


@app.get("/health", tags=["health"])
def health(db: Session = Depends(get_db)):
    """Whether the API can reach its database and find a trained model."""
    try:
        db.execute(text("SELECT 1"))
        database = "ok"
    except SQLAlchemyError:
        database = "unreachable"

    return {
        "status": "ok" if database == "ok" else "degraded",
        "database": database,
        "model_trained": Path(settings.model_path).exists(),
    }
