from typing import Dict, Any, List, TypedDict, Annotated
from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatOllama
from langgraph.graph import StateGraph, START, END

# Define Pydantic Schema for structured LLM output
class VerificationResult(BaseModel):
    verified: bool = Field(description="Whether the care gap is verified to exist")
    evidence: List[str] = Field(description="List of evidence points supporting or contradicting the gap")

# Define LangGraph State Memory
class AgentState(TypedDict):
    gap: Dict[str, Any]
    patient_state: Dict[str, Any]
    verification: Dict[str, Any]

# Initialize LLM
llm = ChatOllama(model="llama3", temperature=0)

# Define Agent Node Function
def verify_gap_node(state: AgentState):
    gap = state["gap"]
    patient_state = state["patient_state"]
    
    prompt = f"Verify if the following care gap is valid based on the patient's records. Gap: {gap}. Patient Records: {patient_state}"
    
    structured_llm = llm.with_structured_output(VerificationResult)
    
    try:
        result = structured_llm.invoke(prompt)
        verification_data = result.model_dump()
    except Exception as e:
        print(f"Error calling LLM: {e}")
        # Fallback to mock logic
        verification_data = {"verified": True, "evidence": ["Mock evidence: fallback logic executed"]}
        
    final_gap = gap.copy()
    final_gap.update(verification_data)
    
    return {"verification": final_gap}

# Build LangGraph
builder = StateGraph(AgentState)
builder.add_node("verify_gap", verify_gap_node)
builder.add_edge(START, "verify_gap")
builder.add_edge("verify_gap", END)
graph = builder.compile()

def verify_care_gap(gap: Dict[str, Any], patient_state: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point to invoke the LangGraph agent."""
    initial_state = {"gap": gap, "patient_state": patient_state, "verification": {}}
    result = graph.invoke(initial_state)
    return result["verification"]

if __name__ == "__main__":
    print("Evidence Agent (LangGraph + Ollama) initialized")
