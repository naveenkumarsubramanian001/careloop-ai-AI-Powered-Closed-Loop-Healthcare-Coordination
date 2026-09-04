import pytest

from app import main
from app.main import collect_evidence_node, verify_care_gap


class FailingModel:
    def with_structured_output(self, schema):
        return self

    def invoke(self, prompt):
        raise RuntimeError("model offline")


def test_collect_evidence_filters_relevant_events():
    result = collect_evidence_node(
        {
            "gap": {"type": "missing_result"},
            "patient_state": {
                "events": [
                    {"event_type": "lab_order", "test": "HbA1c"},
                    {"event_type": "medication", "name": "metformin"},
                ]
            },
        }
    )

    assert len(result["evidence_candidates"]) == 1
    assert "lab_order" in result["evidence_candidates"][0]


def test_verify_care_gap_uses_deterministic_fallback_when_model_fails(monkeypatch):
    monkeypatch.setattr(main, "llm", FailingModel())

    verified = verify_care_gap(
        {"gap_id": "gap-1", "type": "unresolved_referral", "description": "Cardiology referral open"},
        {
            "events": [
                {"event_type": "referral", "specialty": "cardiology"},
                {"event_type": "consultation", "specialty": "cardiology"},
            ]
        },
    )

    assert verified["verified"] is False
    assert verified["verification_source"] == "fallback"
    assert verified["evidence"]


def test_verify_care_gap_keeps_gap_open_without_closing_evidence(monkeypatch):
    monkeypatch.setattr(main, "llm", FailingModel())

    verified = verify_care_gap(
        {"gap_id": "gap-2", "type": "missing_result", "description": "HbA1c result missing"},
        {"events": [{"event_type": "lab_order", "test": "HbA1c"}]},
    )

    assert verified["verified"] is True
    assert verified["confidence"] > 0


def test_verify_care_gap_validates_inputs():
    with pytest.raises(ValueError):
        verify_care_gap({}, {"events": []})

    with pytest.raises(ValueError):
        verify_care_gap({"type": "missing_result"}, [])
