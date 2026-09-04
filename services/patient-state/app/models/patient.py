from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, List, Optional

class PatientModel:
    def __init__(self):
        self.patients: Dict[str, Dict[str, Any]] = {}
        self.events: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = RLock()
        
    def add_patient(self, patient_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if not patient_id or not patient_id.strip():
            raise ValueError("patient_id is required")
        now = datetime.now(timezone.utc).isoformat()
        patient = {
            **data,
            "id": patient_id,
            "updated_at": now,
            "created_at": data.get("created_at", now),
        }
        with self._lock:
            self.patients[patient_id] = patient
            self.events.setdefault(patient_id, [])
            return deepcopy(patient)
        
    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            patient = self.patients.get(patient_id)
            return deepcopy(patient) if patient else None
        
    def add_event(self, patient_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
        if patient_id not in self.patients:
            raise KeyError("Patient not found")
        normalized_event = {
            **event,
            "patient_id": patient_id,
            "created_at": event.get("created_at") or datetime.now(timezone.utc).isoformat(),
        }
        with self._lock:
            self.events.setdefault(patient_id, []).append(normalized_event)
            self.patients[patient_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
            return deepcopy(normalized_event)
        
    def get_events(self, patient_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            return [deepcopy(event) for event in self.events.get(patient_id, [])]

    def build_state(self, patient_id: str) -> Optional[Dict[str, Any]]:
        patient = self.get_patient(patient_id)
        if not patient:
            return None
        events = sorted(self.get_events(patient_id), key=lambda item: item.get("date", ""))
        open_intents = [
            event for event in events
            if event.get("event_type") in {"referral", "investigation", "lab_order", "test_order"}
        ]
        closing_events = [
            event for event in events
            if event.get("event_type") in {"consultation", "specialist_report", "lab_result", "result", "test_result"}
        ]
        return {
            "patient_id": patient_id,
            "patient": patient,
            "events": events,
            "summary": {
                "total_events": len(events),
                "open_intent_count": len(open_intents),
                "closing_event_count": len(closing_events),
                "recent_event": events[-1] if events else None,
            },
        }

patient_db = PatientModel()

# Seed some mock data based on the README example
patient_db.add_patient("P001", {"id": "P001", "name": "John Doe"})
patient_db.add_event("P001", {"event_type": "referral", "specialty": "cardiology", "date": "2026-08-04"})
patient_db.add_event("P001", {"event_type": "investigation", "test": "HbA1c", "date": "2026-08-03"})
