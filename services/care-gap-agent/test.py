import pytest

from app import main
from app.main import detect_care_gaps, llm_detection_node, normalize_state_node, rule_detection_node


class FailingModel:
    def with_structured_output(self, schema):
        return self

    def invoke(self, prompt):
        raise RuntimeError("model offline")


def test_detect_care_gaps_uses_rule_fallback_when_llm_fails(monkeypatch):
    monkeypatch.setattr(main, "llm", FailingModel())

    gaps = detect_care_gaps(
        {
            "patient_id": "P001",
            "events": [
                {"event_type": "referral", "specialty": "cardiology", "date": "2026-08-04"},
                {"event_type": "investigation", "test": "HbA1c", "date": "2026-08-03"},
            ],
        }
    )

    assert {gap["type"] for gap in gaps} == {"unresolved_referral", "missing_result"}
    assert all(0 <= gap["confidence"] <= 1 for gap in gaps)
    assert gaps[0]["confidence"] >= gaps[-1]["confidence"]


def test_normalize_state_rejects_non_list_events():
    result = normalize_state_node({"patient_state": {"events": "bad"}, "errors": []})

    assert result["normalized_events"] == []
    assert "patient_state.events must be a list" in result["errors"]


def test_rule_detection_does_not_flag_closed_referral():
    normalized = [
        {"event_type": "referral", "specialty": "cardiology"},
        {"event_type": "consultation", "specialty": "cardiology"},
    ]

    result = rule_detection_node({"patient_state": {"patient_id": "P001"}, "normalized_events": normalized})

    assert result["rule_based_gaps"] == []


def test_llm_detection_records_errors_on_model_failure(monkeypatch):
    monkeypatch.setattr(main, "llm", FailingModel())

    result = llm_detection_node(
        {
            "normalized_events": [{"event_type": "referral", "specialty": "cardiology"}],
            "errors": [],
        }
    )

    assert result["llm_gaps"] == []
    assert result["errors"][0].startswith("llm_detection_failed")


def test_detect_care_gaps_requires_dictionary_input():
    with pytest.raises(ValueError):
        detect_care_gaps(["not", "a", "dict"])
