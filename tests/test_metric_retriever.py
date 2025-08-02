import pytest
from monitoring_dashboard import MetricRetriever, ModelFactory

class DummyEmbed:
    def embed(self, texts):
        # Возвращаем фиктивный вектор для любого текста
        return [[1.23, 4.56]]

class DummyDB:
    def query(self, vector, top_k=5):
        # Эмулируем выдачу списка метрик
        return [{"metric": "m1"}, {"metric": "m2"}]

@pytest.fixture(autouse=True)
def patch_embedding_model(monkeypatch):
    # Заставляем ModelFactory.get_embedding() возвращать DummyEmbed
    monkeypatch.setattr(
        ModelFactory,
        "get_embedding",
        lambda self: DummyEmbed()
    )

def test_metric_retriever():
    factory = ModelFactory()
    db = DummyDB()
    retr = MetricRetriever(factory, db)
    metrics = retr.retrieve("cpu usage", top_k=2)
    assert metrics == ["m1", "m2"]
