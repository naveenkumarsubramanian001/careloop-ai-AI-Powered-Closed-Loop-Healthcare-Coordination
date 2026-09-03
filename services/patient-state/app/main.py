from fastapi import FastAPI
from app.routes import patients

app = FastAPI(title="CareLoop Patient State Service")

app.include_router(patients.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "patient-state"}
