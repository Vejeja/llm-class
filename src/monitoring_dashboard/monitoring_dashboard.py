import os
import re
import json
import requests
from abc import ABC
from dotenv import load_dotenv, find_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 1) Подгружаем .env 
load_dotenv(find_dotenv())

# 2) Конфигурация API
API_URL = os.getenv("OPENROUTER_API_URL")
EMB_URL = os.getenv("OPENROUTER_EMB_URL")
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not (API_URL and EMB_URL and API_KEY):
    raise RuntimeError("Не найдены OPENROUTER_API_URL/EMB_URL/API_KEY")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

MODELS = {
    "intent":        os.getenv("INTENT_MODEL"),
    "embedding":     os.getenv("EMBEDDING_MODEL"),
    "translator":    os.getenv("TRANSLATOR_MODEL"),
    "query_builder": os.getenv("QUERY_BUILDER_MODEL"),
}


class BaseModel(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name


class LLMModel(BaseModel):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        self.session = session

    def predict(self, prompt: str, temperature: float = 0.0) -> str:
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        r = self.session.post(API_URL, json=payload, headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()


class EmbeddingModel(BaseModel):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        from sentence_transformers import SentenceTransformer
        self.client = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        arr = self.client.encode(texts, convert_to_numpy=True)
        return arr.tolist()


class TranslatorModel(LLMModel):
    def translate_to_en(self, text: str) -> str:
        return self.predict(f"Translate to English: \"{text}\"")
    def translate_to_ru(self, text: str) -> str:
        return self.predict(f"Переведи на русский: \"{text}\"")


class ModelFactory:
    def __init__(self, override: dict[str, str] | None = None):
        cfg = MODELS.copy()
        if override:
            cfg.update(override)
        self.cfg = cfg

    def get_intent(self) -> LLMModel:
        return LLMModel(self.cfg["intent"])
    def get_embedding(self) -> EmbeddingModel:
        return EmbeddingModel(self.cfg["embedding"])
    def get_translator(self) -> TranslatorModel:
        return TranslatorModel(self.cfg["translator"])
    def get_query_builder(self) -> LLMModel:
        return LLMModel(self.cfg["query_builder"])


class IntentParser:
    def __init__(self, factory: ModelFactory | None = None):
        self.client = (factory or ModelFactory()).get_intent()

    def parse(self, user_query: str) -> dict:
        prompt = (
            "Вы — парсер намерений. Верните строго JSON:"
            "{intent, confidence, entities{...}}\n"
            f"Запрос: \"{user_query}\""
        )
        resp = self.client.predict(prompt)
        resp = re.sub(r"^```(?:json)?\s*", "", resp, flags=re.IGNORECASE)
        resp = re.sub(r"\s*```$", "", resp).strip()
        if not resp:
            raise RuntimeError("LLM вернула пустой ответ при intent-парсинге")

        data = json.loads(resp)
        ents = data.get("entities", {})
        for key in ("metric_description_query", "metric", "metric_name", "description"):
            if key in ents:
                ents["metric_description_query"] = ents[key]
                break
        data["entities"] = ents
        return data


class MetricRetriever:
    def __init__(self, factory: ModelFactory | None = None, db_client=None):
        self.embedder = (factory or ModelFactory()).get_embedding()
        self.db = db_client

    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        vec = self.embedder.embed([query])[0]
        results = self.db.query(vec, top_k=top_k)
        return [r["metric"] for r in results]


class PromQLBuilder:
    def __init__(self, factory: ModelFactory | None = None):
        self.client = (factory or ModelFactory()).get_query_builder()

    def build(self, intent_json: dict, metrics: list[str]) -> dict:
        prompt = (
            f"Input JSON: {json.dumps(intent_json)}\n"
            f"Available metrics: {metrics}\n"
            "Верните JSON {status, confidence, reasoning, response{query, message}}"
        )
        resp = self.client.predict(prompt)
        resp = re.sub(r"^```(?:json)?\s*", "", resp, flags=re.IGNORECASE)
        resp = re.sub(r"\s*```$", "", resp).strip()
        return json.loads(resp)

class DummyHfClient:
    """Только для тестов pytest."""
    def __init__(self, model_name: str):
        pass
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]