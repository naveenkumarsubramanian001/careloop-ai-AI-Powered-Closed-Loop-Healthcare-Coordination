from fastapi import FastAPI

from app.config import settings
from app.routes.document import router as document_router

app = FastAPI(
    title="Document Service",
    version=settings.APP_VERSION,
    description="Document retrieval, upload, and metadata management service",
)

app.include_router(document_router)


@app.get("/health", status_code=200)
async def health_check():
    """Health check endpoint to verify the service is running."""
    return {"status": "healthy"}