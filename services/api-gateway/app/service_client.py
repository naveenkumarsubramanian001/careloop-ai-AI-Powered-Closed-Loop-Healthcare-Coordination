import logging
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, UploadFile

from app.config import settings

logger = logging.getLogger(__name__)


class ServiceClient:
    def __init__(self, base_url: str, service_name: str):
        self.base_url = base_url.rstrip("/")
        self.service_name = service_name

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
                response = await client.request(method, url, json=json, params=params, data=data, files=files)
        except httpx.TimeoutException as exc:
            logger.warning("service_timeout", extra={"service": self.service_name, "url": url})
            raise HTTPException(status_code=504, detail=f"{self.service_name} timed out") from exc
        except httpx.HTTPError as exc:
            logger.warning("service_unavailable", extra={"service": self.service_name, "url": url, "error": str(exc)})
            raise HTTPException(status_code=503, detail=f"{self.service_name} is unavailable") from exc

        if response.status_code >= 400:
            detail = _response_detail(response)
            raise HTTPException(status_code=response.status_code, detail=detail)

        if not response.content:
            return None
        return response.json()

    async def upload(self, path: str, *, patient_id: str, file: UploadFile) -> Any:
        content = await file.read()
        files = {"file": (file.filename, content, file.content_type)}
        data = {"patient_id": patient_id}
        return await self.request("POST", path, data=data, files=files)


def _response_detail(response: httpx.Response) -> Any:
    try:
        payload = response.json()
    except ValueError:
        return response.text or "Upstream service error"
    return payload.get("detail", payload)


document_client = ServiceClient(settings.document_service_url, "document-service")
patient_client = ServiceClient(settings.patient_state_url, "patient-state")
task_client = ServiceClient(settings.task_service_url, "task-service")
