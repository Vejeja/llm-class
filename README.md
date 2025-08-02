# Dashboard-LLM

---

## 📁 Структура проекта

- `src/monitoring_dashboard/` — весь основной код:
  - Разбор естественного языка → JSON-интент
  - Построение эмбеддингов
  - Выбор метрик из БД
  - Сборка финального PromQL
- `src/main.py` — точка входа CLI (скрипт `monitoring-dashboard`)
- `tests/` — unit-тесты с `pytest` и `monkeypatch`

---

## 📚 Реализация модуля `monitoring_dashboard`

Внутри `src/monitoring_dashboard/monitoring_dashboard.py` реализованы следующие классы:

### `DummyHfClient`
Небольшой тестовый «заглушечный» клиент для эмбеддингов:
- **Метод** `embed_documents(texts: list[str]) -> list[list[float]]`  
  Возвращает всегда фиксированные векторы.  
- Используется в unit-тестах для подмены реального Sentence-Transformer.

---

### `BaseModel`
Абстрактный класс:
- Хранит единственное поле `model_name` (имя модели из `.env` или override).
- Служит базой для всех LLM- и эмбеддинг-клиентов.

---

### `LLMModel(BaseModel)`
Клиент для любых чат-моделей (Intent, QueryBuilder, Translator):
1. Формирует payload вида:
   ```json
   {
     "model": model_name,
     "messages": [{"role":"user","content": prompt}],
     "temperature": 0.0
   }
   ```

2. `requests.post(API_URL, json=payload, headers=...)`
3. Проверяет HTTP-код, ловит и логирует ошибки.
4. Парсит JSON-ответ, возвращает `choices[0].message.content.strip()`.

---

### `EmbeddingModel(BaseModel)`

Локальный эмбеддинг-клиент через `sentence-transformers`:

1. В конструкторе загружает `SentenceTransformer(model_name)`.
2. Метод `embed(texts: list[str])` кодирует список текстов:

   ```python
   embs = self.client.encode(texts, convert_to_numpy=True)
   return embs.tolist()
   ```

---

### `TranslatorModel(LLMModel)`

Простой обёртка над `LLMModel` для перевода:

* `translate_to_en(text: str) -> str`
  вызывает `predict("Translate to English: …")`
* `translate_to_ru(text: str) -> str`
  вызывает `predict("Переведи на русский: …")`

---

### `ModelFactory`

Управляет конфигурацией моделей:

* Читает из `MODELS = { intent, embedding, translator, query_builder }`
* Позволяет через `--override key=value` заменить любую модель.
* Методы `.get_intent()`, `.get_embedding()`, `.get_translator()`, `.get_query_builder()`
  возвращают соответствующие экземпляры клиентов.

---

### `IntentParser`

Преобразует текстовый запрос в структурированный JSON-интент:

1. Строит prompt:

   ```
   Вы — парсер намерений. Верните строго JSON:{intent, confidence, entities{...}}
   Запрос: "…"
   ```
2. Вызывает `LLMModel.predict()`.
3. Убирает Markdown-ограничители `json …`.
4. Парсит в Python-словарь.
5. Нормализует ключи сущностей:
   если в `entities` есть любой из `metric_description_query`, `metric`, `metric_name`, `description` —
   переименовывает его в `metric_description_query`.

---

### `MetricRetriever`

Извлекает «ближайшие по смыслу» метрики из любой векторной БД:

1. Запрашивает эмбеддинг via `EmbeddingModel.embed([query])`.
2. Передаёт вектор в `db_client.query(vector, top_k)`.
3. Возвращает список строковых имён метрик.

---

### `PromQLBuilder`

Генерирует финальный PromQL-запрос:

1. Формирует prompt:

   ```
   Input JSON: {…intent JSON…}
   Available metrics: […]
   Верните JSON {status, confidence, reasoning, response{query, message}}
   ```
2. Вызывает `LLMModel.predict()`.
3. Убирает Markdown-ограничители.
4. Парсит JSON-ответ и возвращает словарь:

   ```json
   {
     "status": "success",
     "confidence": 0.95,
     "reasoning": "...",
     "response": { "query": "...", "message": "..." }
   }
   ```

---

## ⚙️ Установка зависимостей

```bash
git clone <repo_url>
cd dashboard-llm
poetry install
```

## 🔧 Настройка

```bash
cp .env.example .env
```

## 🚀 Запуск CLI

```bash
poetry run monitoring-dashboard "Покажи CPU за последний час"
```

---

## ✅ Тестирование

```bash
poetry run pytest
```