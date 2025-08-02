# Dashboard-LLM


## 📁 Структура проекта

- `src/monitoring_dashboard/` — вся логика: парсинг intent, построение эмбеддингов, сборка PromQL  
- `src/main.py` — точка входа CLI (установлена как `monitoring-dashboard`)  
- `tests/` — unit-тесты с `pytest` и `monkeypatch` для заглушек LLM/эмбеддингов  

---

## ⚙️ Установка зависимостей

1. Склонировать репозиторий:
   ```bash
   git clone <repo_url>
   cd dashboard-llm
   ```

2. Установить Poetry (если ещё не установлен):

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Установить зависимости:

   ```bash
   poetry install
   ```

4. Активировать виртуальное окружение (опционально):

   ```bash
   poetry shell
   ```

---

## 🔧 Настройка

1. Скопировать шаблон `.env.example` в `.env`:

   ```bash
   cp .env.example .env
   ```

2. Заполнить в `.env` свои ключи и модели:

   ```dotenv
   OPENROUTER_API_KEY=ваш_ключ
   OPENROUTER_API_URL=https://openrouter.ai/api/v1/chat/completions
   OPENROUTER_EMB_URL=https://openrouter.ai/api/v1/embeddings

   INTENT_MODEL=…
   EMBEDDING_MODEL=…
   TRANSLATOR_MODEL=…
   QUERY_BUILDER_MODEL=…
   ```

---

## 🚀 Запуск

После установки и настройки ENV просто выполнить:

```bash
poetry run monitoring-dashboard "Покажи CPU за последний час"
```

Или, если вы в `poetry shell`:

```bash
monitoring-dashboard "Покажи CPU за последний час"
```

---

## ✅ Тестирование

Все ключевые компоненты покрыты unit-тестами. Запустить можно командой:

```bash
poetry run pytest
```