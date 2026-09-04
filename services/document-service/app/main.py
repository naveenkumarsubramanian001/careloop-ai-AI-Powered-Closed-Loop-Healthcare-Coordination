import logging

from fastapi import FastAPI
from app.routes import documents

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="CareLoop Document Service")

app.include_router(documents.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "document-service"}
