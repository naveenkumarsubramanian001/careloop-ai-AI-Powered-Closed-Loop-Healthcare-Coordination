import pytest

from app import main
from app.main import generate_action, prepare_context_node


class FailingModel:
    def with_structured_output(self, schema):
        return self

    def invoke(self, prompt):
        raise RuntimeError("model offline")


def test_prepare_context_sets_high_priority_for_confident_gap():
    result = prepare_context_node(
        {
            "verified_gap": {
                "type": "missing_result",
                "confidence": 0.91,
            }
        }
    )

    assert result["context"]["priority"] == "High"
    assert "lab" in result["context"]["default_action"].lower()


def test_generate_action_falls_back_to_operational_recommendation(monkeypatch):
    monkeypatch.setattr(main, "llm", FailingModel())

    action = generate_action(
        {
            "gap_id": "gap-1",
            "type": "unresolved_referral",
            "description": "Cardiology referral unresolved",
            "confidence": 0.88,
            "verified": True,
        }
    )

    assert action["action_source"] == "fallback"
    assert action["priority"] == "High"
    assert action["assigned_to"] == "Care Coordinator"
    assert "appointment" in action["action_recommendation"].lower()


def test_generate_action_requires_non_empty_gap():
    with pytest.raises(ValueError):
        generate_action({})
