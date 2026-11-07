from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import engine
from app.routers.jobs import router as job_router
from app.routers.auth import router as auth_router
from app.routers.dashboard import router as dashboard_router

app = FastAPI(title="Job Tracker API")

app.include_router(job_router)
app.include_router(auth_router)
app.include_router(dashboard_router)

@app.get("/")
def root():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"database": result.scalar()}

    