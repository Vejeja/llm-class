import pytest
import monitoring_dashboard
from monitoring_dashboard import EmbeddingModel, DummyHfClient

class DummyHfClient:
    def __init__(self, model_name):
        pass
    def embed_documents(self, texts):
        return [[0.1,0.2,0.3],[0.4,0.5,0.6]]

@pytest.fixture(autouse=True)
def patch_hf(monkeypatch):
    def fake_init(self, model_name):
        self.client = DummyHfClient(model_name)
    monkeypatch.setattr(
        monitoring_dashboard.EmbeddingModel,
        '__init__',
        fake_init
    )

def test_embedding_model():
    emb = EmbeddingModel("dummy-model")
    vectors = emb.embed(["text1", "text2"])
    assert isinstance(vectors, list)
    assert len(vectors) == 2
    assert vectors[0] == [0.1, 0.2, 0.3]
    assert vectors[1] == [0.4, 0.5, 0.6]
