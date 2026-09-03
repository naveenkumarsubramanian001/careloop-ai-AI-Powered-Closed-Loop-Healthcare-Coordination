from fastapi import FastAPI
from app.routes import tasks

app = FastAPI(title="CareLoop Task Service")

app.include_router(tasks.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "task-service"}
