from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    document_service_url: str = os.getenv("DOCUMENT_SERVICE_URL", "http://document-service:8001")
    patient_state_url: str = os.getenv("PATIENT_STATE_URL", "http://patient-state:8003")
    task_service_url: str = os.getenv("TASK_SERVICE_URL", "http://task-service:8004")
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "5"))


settings = Settings()
