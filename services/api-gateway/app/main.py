from fastapi import FastAPI
from app.routes import documents, patients, care_gaps, tasks

app = FastAPI(title="CareLoop API Gateway")

app.include_router(documents.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(care_gaps.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "api-gateway"}
