from typing import List, Dict, Any

class PatientModel:
    def __init__(self):
        self.patients = {}
        self.events = {}
        
    def add_patient(self, patient_id: str, data: Dict[str, Any]):
        self.patients[patient_id] = data
        
    def get_patient(self, patient_id: str) -> Dict[str, Any]:
        return self.patients.get(patient_id)
        
    def add_event(self, patient_id: str, event: Dict[str, Any]):
        if patient_id not in self.events:
            self.events[patient_id] = []
        self.events[patient_id].append(event)
        
    def get_events(self, patient_id: str) -> List[Dict[str, Any]]:
        return self.events.get(patient_id, [])

patient_db = PatientModel()

# Seed some mock data based on the README example
patient_db.add_patient("P001", {"id": "P001", "name": "John Doe"})
patient_db.add_event("P001", {"event_type": "referral", "specialty": "cardiology", "date": "2026-08-04"})
patient_db.add_event("P001", {"event_type": "investigation", "test": "HbA1c", "date": "2026-08-03"})
