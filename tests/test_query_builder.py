import pytest
import json
from monitoring_dashboard import PromQLBuilder, ModelFactory

class DummyLLM:
    def predict(self, prompt: str, temperature: float = 0.0) -> str:
        # Эмулируем ответ билдера PromQL
        return json.dumps({
            "status": "success",
            "confidence": 0.8,
            "reasoning": "simple reasoning",
            "response": {
                "query": "up",
                "message": "ok"
            }
        })

@pytest.fixture(autouse=True)
def patch_query_builder(monkeypatch):
    # Заставляем ModelFactory.get_query_builder() возвращать DummyLLM
    monkeypatch.setattr(
        ModelFactory,
        "get_query_builder",
        lambda self: DummyLLM()
    )

def test_query_builder():
    builder = PromQLBuilder()
    intent_json = {
        "intent": "get_timeseries_metric",
        "entities": {"metric_description_query": "cpu"}
    }
    metrics = ["m1", "m2"]
    result = builder.build(intent_json, metrics)
    assert result["status"] == "success"
    assert result["response"]["query"] == "up"
    assert result["confidence"] == pytest.approx(0.8)
