from fastapi import Depends ,FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.auth import router as auth_router

from app.database.database import get_db

app = FastAPI(
    title="auth-service",
    description="Authentication and Authorization API",
    version="1.0.0",
)
app.include_router(auth_router)
@app.get("/")
def root():
    return {
        "service": "AuthService",
        "status": "running",
    }

@app.get("/health")
def health():
    return{
        "status": "healthy"
    }

@app.get("/database/health")
def database_health(
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("SELECT 1")
    )
    return {
        "database": "PostgreSQL",
        "status": "connected",
        "result": result.scalar()
    }


