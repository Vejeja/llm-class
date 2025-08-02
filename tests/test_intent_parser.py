import pytest
import json
from monitoring_dashboard import IntentParser, ModelFactory

class DummyLLM:
    def predict(self, prompt: str, temperature: float = 0.0) -> str:
        return json.dumps({
            "intent": "get_timeseries_metric",
            "confidence": 0.92,
            "entities": {
                "metric_description_query": "cpu usage",
                "time_range": {"unit": "hours", "value": 1}
            }
        })

@pytest.fixture(autouse=True)
def patch_intent_model(monkeypatch):
    monkeypatch.setattr(
        ModelFactory,
        "get_intent",
        lambda self: DummyLLM()
    )

def test_intent_parser():
    parser = IntentParser()
    result = parser.parse("Покажи CPU за последний час")
    assert result["intent"] == "get_timeseries_metric"
    assert result["confidence"] == pytest.approx(0.92)
    assert result["entities"]["metric_description_query"] == "cpu usage"
    assert result["entities"]["time_range"]["value"] == 1
