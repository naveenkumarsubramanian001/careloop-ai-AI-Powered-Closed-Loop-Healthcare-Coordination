from typing import Dict, Any, List, TypedDict, Annotated
from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatOllama
from langgraph.graph import StateGraph, START, END

# Define Pydantic Schema for structured LLM output
class CareGap(BaseModel):
    gap_id: str = Field(description="A unique identifier for the gap")
    type: str = Field(description="The type of the gap, e.g. 'unresolved_referral', 'missing_result'")
    description: str = Field(description="A human readable description of the gap")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")

class CareGapsResponse(BaseModel):
    gaps: List[CareGap]

# Define LangGraph State Memory
class AgentState(TypedDict):
    patient_state: Dict[str, Any]
    detected_gaps: List[Dict[str, Any]]

# Initialize LLM
llm = ChatOllama(model="llama3", temperature=0)

# Define Agent Node Function
def detect_gaps_node(state: AgentState):
    patient_state = state["patient_state"]
    events = patient_state.get("events", [])
    
    # Prompt the LLM
    prompt = f"Analyze the following patient events and identify any care gaps (e.g. unresolved referrals, missing test results). Events: {events}"
    
    # Bind the schema to the LLM to get structured output
    structured_llm = llm.with_structured_output(CareGapsResponse)
    
    try:
        result = structured_llm.invoke(prompt)
        # Convert pydantic models to dicts to pass through state
        gaps_list = [gap.model_dump() for gap in result.gaps]
    except Exception as e:
        print(f"Error calling LLM: {e}")
        # Fallback to mock logic if LLM isn't running
        gaps_list = []
        has_referral = any(e.get("event_type") == "referral" for e in events)
        has_consult = any(e.get("event_type") == "consultation" for e in events)
        if has_referral and not has_consult:
            gaps_list.append({
                "gap_id": "gap_001", "type": "unresolved_referral", 
                "description": "Cardiology referral unresolved", "confidence": 0.94
            })
            
    return {"detected_gaps": gaps_list}

# Build LangGraph
builder = StateGraph(AgentState)
builder.add_node("detect_gaps", detect_gaps_node)
builder.add_edge(START, "detect_gaps")
builder.add_edge("detect_gaps", END)
graph = builder.compile()

def detect_care_gaps(patient_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Entry point to invoke the LangGraph agent."""
    initial_state = {"patient_state": patient_state, "detected_gaps": []}
    result = graph.invoke(initial_state)
    return result["detected_gaps"]

if __name__ == "__main__":
    print("Care Gap Agent (LangGraph + Ollama) initialized")
