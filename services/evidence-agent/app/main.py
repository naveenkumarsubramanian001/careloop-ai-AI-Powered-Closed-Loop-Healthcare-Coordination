import logging
import os
from typing import Any, Dict, List, TypedDict

from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatOllama
from langgraph.graph import StateGraph, START, END

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


class VerificationResult(BaseModel):
    verified: bool = Field(description="Whether the care gap is verified to exist")
    evidence: List[str] = Field(default_factory=list, description="Evidence points supporting or contradicting the gap")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str = ""


class AgentState(TypedDict):
    gap: Dict[str, Any]
    patient_state: Dict[str, Any]
    evidence_candidates: List[str]
    llm_verification: Dict[str, Any]
    verification: Dict[str, Any]
    errors: List[str]


def build_llm() -> ChatOllama:
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        temperature=0,
        base_url=os.getenv("OLLAMA_BASE_URL"),
    )


llm = build_llm()


def collect_evidence_node(state: AgentState) -> Dict[str, Any]:
    gap = state["gap"]
    patient_state = state["patient_state"]
    gap_type = str(gap.get("type", "")).lower()
    events = patient_state.get("events") or []
    candidates: List[str] = []

    if isinstance(events, list):
        for event in events:
            if not isinstance(event, dict):
                continue
            event_type = str(event.get("event_type", "")).lower()
            if gap_type == "unresolved_referral" and event_type in {"referral", "consultation", "specialist_report"}:
                candidates.append(f"{event_type}: {event}")
            elif gap_type == "missing_result" and event_type in {"investigation", "lab_order", "lab_result", "result"}:
                candidates.append(f"{event_type}: {event}")

    return {"evidence_candidates": candidates}


def llm_verify_node(state: AgentState) -> Dict[str, Any]:
    gap = state["gap"]
    patient_state = state["patient_state"]
    evidence_candidates = state.get("evidence_candidates", [])
    if not evidence_candidates:
        return {
            "llm_verification": VerificationResult(
                verified=True,
                confidence=0.55,
                evidence=["No closing evidence found in patient timeline."],
                reason="Rule fallback: absence of counter-evidence keeps the gap open.",
            ).model_dump()
        }

    prompt = (
        "Verify whether the care gap still exists using only the patient records. "
        "Mark verified=false when records clearly close the gap. "
        f"Gap: {gap}. Candidate evidence: {evidence_candidates}. Patient Records: {patient_state}"
    )
    structured_llm = llm.with_structured_output(VerificationResult)

    try:
        result = structured_llm.invoke(prompt)
        verification_data = result.model_dump()
    except Exception as e:
        logger.exception("evidence_llm_failed")
        verification_data = _rule_based_verification(gap, evidence_candidates)
        return {
            "llm_verification": verification_data,
            "errors": [*state.get("errors", []), f"llm_verification_failed: {e}"],
        }

    return {"llm_verification": verification_data}


def _rule_based_verification(gap: Dict[str, Any], evidence_candidates: List[str]) -> Dict[str, Any]:
    gap_type = str(gap.get("type", "")).lower()
    closing_terms = {
        "unresolved_referral": ("consultation", "specialist_report", "completed"),
        "missing_result": ("lab_result", "result", "resulted"),
    }.get(gap_type, ("closed", "completed"))
    has_closing_evidence = any(term in candidate.lower() for term in closing_terms for candidate in evidence_candidates)
    return VerificationResult(
        verified=not has_closing_evidence,
        confidence=0.72 if evidence_candidates else 0.55,
        evidence=evidence_candidates or ["No relevant timeline evidence was available."],
        reason="Deterministic fallback verification.",
    ).model_dump()


def finalize_verification_node(state: AgentState) -> Dict[str, Any]:
    verification_data = VerificationResult.model_validate(state.get("llm_verification", {})).model_dump()
    gap = state["gap"]
    final_gap = gap.copy()
    final_gap.update(verification_data)
    final_gap["verification_source"] = "llm" if not state.get("errors") else "fallback"
    return {"verification": final_gap}


builder = StateGraph(AgentState)
builder.add_node("collect_evidence", collect_evidence_node)
builder.add_node("llm_verify", llm_verify_node)
builder.add_node("finalize_verification", finalize_verification_node)
builder.add_edge(START, "collect_evidence")
builder.add_edge("collect_evidence", "llm_verify")
builder.add_edge("llm_verify", "finalize_verification")
builder.add_edge("finalize_verification", END)
graph = builder.compile()


def verify_care_gap(gap: Dict[str, Any], patient_state: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point to invoke the LangGraph agent."""
    if not isinstance(gap, dict) or not gap:
        raise ValueError("gap must be a non-empty dictionary")
    if not isinstance(patient_state, dict):
        raise ValueError("patient_state must be a dictionary")

    initial_state = {
        "gap": gap,
        "patient_state": patient_state,
        "evidence_candidates": [],
        "llm_verification": {},
        "verification": {},
        "errors": [],
    }
    result = graph.invoke(initial_state)
    return result["verification"]

if __name__ == "__main__":
    logger.info("Evidence Agent (LangGraph + Ollama) initialized")
