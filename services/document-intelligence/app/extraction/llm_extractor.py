from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatOllama

class ClinicalEvent(BaseModel):
    event_type: str
    details: str
    date: str
    confidence: float

class ClinicalEventsResponse(BaseModel):
    events: List[ClinicalEvent]

llm = ChatOllama(model="llama3", temperature=0)

def extract_clinical_events(text: str) -> List[Dict[str, Any]]:
    """Ollama LLM extraction to get structured clinical events from text."""
    prompt = f"Extract all clinical events from the following text: {text}"
    structured_llm = llm.with_structured_output(ClinicalEventsResponse)
    
    try:
        result = structured_llm.invoke(prompt)
        return [e.model_dump() for e in result.events]
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return []
