import logging
import os
from typing import Any, Dict, List

from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatOllama

logger = logging.getLogger(__name__)


class ClinicalEvent(BaseModel):
    event_type: str
    details: str
    date: str
    confidence: float = Field(ge=0.0, le=1.0)

class ClinicalEventsResponse(BaseModel):
    events: List[ClinicalEvent] = Field(default_factory=list)


def build_llm() -> ChatOllama:
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        temperature=0,
        base_url=os.getenv("OLLAMA_BASE_URL"),
    )


llm = build_llm()


def extract_clinical_events(text: str, model: Any = None) -> List[Dict[str, Any]]:
    """Ollama LLM extraction to get structured clinical events from text."""
    if not text or not text.strip():
        return []

    active_model = model or llm
    prompt = (
        "Extract clinical events from the text. Keep event_type normalized, include dates when present, "
        f"and return confidence for each event. Text: {text[:12000]}"
    )
    structured_llm = active_model.with_structured_output(ClinicalEventsResponse)
    
    try:
        result = structured_llm.invoke(prompt)
        return [e.model_dump() for e in result.events]
    except Exception:
        logger.exception("clinical_event_llm_failed")
        return _fallback_extract_events(text)


def _fallback_extract_events(text: str) -> List[Dict[str, Any]]:
    normalized = text.lower()
    events: List[Dict[str, Any]] = []
    if "referral" in normalized:
        specialty = "cardiology" if "cardiology" in normalized else None
        events.append(
            {
                "event_type": "referral",
                "details": "Referral mentioned in source document.",
                "date": "",
                "confidence": 0.62,
                "specialty": specialty,
                "source": "fallback",
            }
        )
    if any(term in normalized for term in ("hba1c", "lab", "test ordered", "ordered")):
        events.append(
            {
                "event_type": "investigation",
                "details": "Investigation or lab order mentioned in source document.",
                "date": "",
                "confidence": 0.58,
                "test": "HbA1c" if "hba1c" in normalized else None,
                "source": "fallback",
            }
        )
    return events
