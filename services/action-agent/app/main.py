import logging
import os
from typing import Any, Dict, List, TypedDict

from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatOllama
from langgraph.graph import StateGraph, START, END

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


class ActionRecommendation(BaseModel):
    action_recommendation: str = Field(description="The recommended next step to resolve the care gap")
    priority: str = Field(default="Medium", description="Operational priority: Low, Medium, High, or Urgent")
    assigned_to: str = Field(default="Care Coordinator")
    rationale: str = Field(default="")


class AgentState(TypedDict):
    verified_gap: Dict[str, Any]
    context: Dict[str, Any]
    recommendation: Dict[str, Any]
    final_action: Dict[str, Any]
    errors: List[str]


def build_llm() -> ChatOllama:
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        temperature=0,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )


llm = build_llm()


def prepare_context_node(state: AgentState) -> Dict[str, Any]:
    verified_gap = state["verified_gap"]
    gap_type = str(verified_gap.get("type", "")).lower()
    confidence = float(verified_gap.get("confidence", 0.0) or 0.0)
    priority = "High" if confidence >= 0.85 else "Medium"
    if gap_type == "missing_result":
        default_action = "Contact the ordering clinic or lab to confirm whether the result is available externally."
    elif gap_type == "unresolved_referral":
        default_action = "Confirm appointment status with the patient or referred specialty office."
    else:
        default_action = "Review the patient record and confirm the next operational step."

    return {"context": {"default_action": default_action, "priority": priority}}


def llm_action_node(state: AgentState) -> Dict[str, Any]:
    verified_gap = state["verified_gap"]
    context = state.get("context", {})
    prompt = (
        "Recommend one concrete operational next step for a healthcare care coordinator. "
        "Do not provide diagnosis or clinical treatment advice. "
        f"Verified gap: {verified_gap}. Default operational context: {context}"
    )
    structured_llm = llm.with_structured_output(ActionRecommendation)

    try:
        result = structured_llm.invoke(prompt)
        recommendation = result.model_dump()
    except Exception as e:
        logger.exception("action_llm_failed")
        recommendation = ActionRecommendation(
            action_recommendation=context.get("default_action", "Verify the status manually."),
            priority=context.get("priority", "Medium"),
            assigned_to="Care Coordinator",
            rationale="Deterministic fallback because the recommendation model was unavailable.",
        ).model_dump()
        return {"recommendation": recommendation, "errors": [*state.get("errors", []), f"llm_action_failed: {e}"]}

    return {"recommendation": recommendation}


def finalize_action_node(state: AgentState) -> Dict[str, Any]:
    recommendation = ActionRecommendation.model_validate(state.get("recommendation", {})).model_dump()
    verified_gap = state["verified_gap"]
    final_action = verified_gap.copy()
    final_action.update(recommendation)
    final_action["action_source"] = "llm" if not state.get("errors") else "fallback"
    return {"final_action": final_action}


builder = StateGraph(AgentState)
builder.add_node("prepare_context", prepare_context_node)
builder.add_node("llm_action", llm_action_node)
builder.add_node("finalize_action", finalize_action_node)
builder.add_edge(START, "prepare_context")
builder.add_edge("prepare_context", "llm_action")
builder.add_edge("llm_action", "finalize_action")
builder.add_edge("finalize_action", END)
graph = builder.compile()


def generate_action(verified_gap: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point to invoke the LangGraph agent."""
    if not isinstance(verified_gap, dict) or not verified_gap:
        raise ValueError("verified_gap must be a non-empty dictionary")

    initial_state = {
        "verified_gap": verified_gap,
        "context": {},
        "recommendation": {},
        "final_action": {},
        "errors": [],
    }
    result = graph.invoke(initial_state)
    return result["final_action"]

if __name__ == "__main__":
    logger.info("Action Agent (LangGraph + Ollama) initialized")
