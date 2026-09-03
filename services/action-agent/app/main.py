from typing import Dict, Any, TypedDict
from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatOllama
from langgraph.graph import StateGraph, START, END

# Define Pydantic Schema
class ActionRecommendation(BaseModel):
    action_recommendation: str = Field(description="The recommended next step to resolve the care gap")

# Define LangGraph State Memory
class AgentState(TypedDict):
    verified_gap: Dict[str, Any]
    final_action: Dict[str, Any]

# Initialize LLM
llm = ChatOllama(model="llama3", temperature=0)

# Define Agent Node Function
def generate_action_node(state: AgentState):
    verified_gap = state["verified_gap"]
    
    prompt = f"Based on this verified care gap, what is the best operational next step for a care coordinator? Gap: {verified_gap}"
    
    structured_llm = llm.with_structured_output(ActionRecommendation)
    
    try:
        result = structured_llm.invoke(prompt)
        action_text = result.action_recommendation
    except Exception as e:
        print(f"Error calling LLM: {e}")
        action_text = "Verify the status manually (fallback)."
        
    final_action = verified_gap.copy()
    final_action["action_recommendation"] = action_text
    
    return {"final_action": final_action}

# Build LangGraph
builder = StateGraph(AgentState)
builder.add_node("generate_action", generate_action_node)
builder.add_edge(START, "generate_action")
builder.add_edge("generate_action", END)
graph = builder.compile()

def generate_action(verified_gap: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point to invoke the LangGraph agent."""
    initial_state = {"verified_gap": verified_gap, "final_action": {}}
    result = graph.invoke(initial_state)
    return result["final_action"]

if __name__ == "__main__":
    print("Action Agent (LangGraph + Ollama) initialized")
