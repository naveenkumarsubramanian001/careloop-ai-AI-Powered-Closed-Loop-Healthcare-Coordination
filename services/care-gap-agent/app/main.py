import logging
import os
from hashlib import sha1
from typing import Any, Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatOllama
from langgraph.graph import StateGraph, START, END

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


class CareGap(BaseModel):
    gap_id: str = Field(description="A unique identifier for the gap")
    type: str = Field(description="The type of the gap, e.g. 'unresolved_referral', 'missing_result'")
    description: str = Field(description="A human readable description of the gap")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    source: str = Field(default="llm", description="Detection source")

class CareGapsResponse(BaseModel):
    gaps: List[CareGap] = Field(default_factory=list)


class AgentState(TypedDict):
    patient_state: Dict[str, Any]
    normalized_events: List[Dict[str, Any]]
    rule_based_gaps: List[Dict[str, Any]]
    llm_gaps: List[Dict[str, Any]]
    detected_gaps: List[Dict[str, Any]]
    errors: List[str]


def build_llm() -> ChatOllama:
    """Create the chat model at runtime so tests can inject a fake graph/model."""
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        temperature=0,
        base_url=os.getenv("OLLAMA_BASE_URL"),
    )


llm = build_llm()


def _stable_gap_id(patient_id: str, gap_type: str, subject: str) -> str:
    digest = sha1(f"{patient_id}:{gap_type}:{subject}".encode("utf-8")).hexdigest()[:10]
    return f"gap_{digest}"


def _clean_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    event_type = str(event.get("event_type") or event.get("type") or "").strip().lower()
    if not event_type:
        return None
    return {
        **event,
        "event_type": event_type,
        "specialty": str(event.get("specialty", "")).strip().lower(),
        "test": str(event.get("test", "")).strip().lower(),
        "date": str(event.get("date", "")).strip(),
    }


def normalize_state_node(state: AgentState) -> Dict[str, Any]:
    patient_state = state["patient_state"]
    events = patient_state.get("events") or []
    if not isinstance(events, list):
        return {
            "normalized_events": [],
            "errors": ["patient_state.events must be a list"],
        }

    normalized_events = [
        cleaned
        for event in events
        if isinstance(event, dict)
        for cleaned in [_clean_event(event)]
        if cleaned is not None
    ]
    return {"normalized_events": normalized_events}


def rule_detection_node(state: AgentState) -> Dict[str, Any]:
    patient_state = state["patient_state"]
    patient_id = str(patient_state.get("patient_id") or patient_state.get("id") or "unknown")
    events = state.get("normalized_events", [])
    gaps: List[Dict[str, Any]] = []

    referral_specialties = {
        event.get("specialty") or "unspecified"
        for event in events
        if event.get("event_type") == "referral"
    }
    completed_specialties = {
        event.get("specialty") or "unspecified"
        for event in events
        if event.get("event_type") in {"consultation", "specialist_report", "visit"}
    }
    for specialty in sorted(referral_specialties - completed_specialties):
        gaps.append(
            CareGap(
                gap_id=_stable_gap_id(patient_id, "unresolved_referral", specialty),
                type="unresolved_referral",
                description=f"{specialty.title()} referral appears unresolved.",
                confidence=0.86,
                source="rules",
            ).model_dump()
        )

    ordered_tests = {
        event.get("test") or "unspecified"
        for event in events
        if event.get("event_type") in {"investigation", "lab_order", "test_order"}
    }
    resulted_tests = {
        event.get("test") or "unspecified"
        for event in events
        if event.get("event_type") in {"lab_result", "result", "test_result"}
    }
    for test_name in sorted(ordered_tests - resulted_tests):
        gaps.append(
            CareGap(
                gap_id=_stable_gap_id(patient_id, "missing_result", test_name),
                type="missing_result",
                description=f"{test_name.upper()} was ordered but no result is present.",
                confidence=0.82,
                source="rules",
            ).model_dump()
        )

    return {"rule_based_gaps": gaps}


def llm_detection_node(state: AgentState) -> Dict[str, Any]:
    events = state.get("normalized_events", [])
    if not events:
        return {"llm_gaps": []}

    prompt = (
        "Analyze the patient event timeline and identify unresolved care gaps. "
        "Return only gaps that are operationally actionable and include confidence. "
        f"Events: {events}"
    )
    structured_llm = llm.with_structured_output(CareGapsResponse)

    try:
        result = structured_llm.invoke(prompt)
        gaps_list = [gap.model_dump() for gap in result.gaps]
    except Exception as e:
        logger.exception("care_gap_llm_failed")
        gaps_list = []
        errors = [*state.get("errors", []), f"llm_detection_failed: {e}"]
        return {"llm_gaps": gaps_list, "errors": errors}

    return {"llm_gaps": gaps_list}


def merge_gaps_node(state: AgentState) -> Dict[str, Any]:
    merged: Dict[str, Dict[str, Any]] = {}
    for gap in [*state.get("rule_based_gaps", []), *state.get("llm_gaps", [])]:
        try:
            validated = CareGap.model_validate(gap).model_dump()
        except Exception as e:
            logger.info("dropping_invalid_gap", extra={"gap": gap, "error": str(e)})
            continue
        key = f"{validated['type']}:{validated['description'].lower()}"
        if key not in merged or validated["confidence"] > merged[key]["confidence"]:
            merged[key] = validated

    return {"detected_gaps": sorted(merged.values(), key=lambda item: item["confidence"], reverse=True)}


builder = StateGraph(AgentState)
builder.add_node("normalize_state", normalize_state_node)
builder.add_node("rule_detection", rule_detection_node)
builder.add_node("llm_detection", llm_detection_node)
builder.add_node("merge_gaps", merge_gaps_node)
builder.add_edge(START, "normalize_state")
builder.add_edge("normalize_state", "rule_detection")
builder.add_edge("rule_detection", "llm_detection")
builder.add_edge("llm_detection", "merge_gaps")
builder.add_edge("merge_gaps", END)
graph = builder.compile()


def detect_care_gaps(patient_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Entry point to invoke the LangGraph agent."""
    if not isinstance(patient_state, dict):
        raise ValueError("patient_state must be a dictionary")

    initial_state = {
        "patient_state": patient_state,
        "normalized_events": [],
        "rule_based_gaps": [],
        "llm_gaps": [],
        "detected_gaps": [],
        "errors": [],
    }
    result = graph.invoke(initial_state)
    return result["detected_gaps"]

if __name__ == "__main__":
    logger.info("Care Gap Agent (LangGraph + Ollama) initialized")
