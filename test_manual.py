from monitoring_dashboard import ModelFactory

def main():
    factory = ModelFactory()

    # 1) Переводчик
    translator = factory.get_translator()
    ru = "Всем привет!"
    en = translator.translate_to_en(ru)
    back = translator.translate_to_ru(en)
    print("=== Translator ===")
    print(f"Оригинал (RU): {ru}")
    print(f"Перевод → EN:  {en}")
    print(f"Перевод ← RU:  {back}\n")

    # 2) LLM
    llm = factory.get_intent()
    question = "Какого цвета трава?"
    answer = llm.predict(question)
    print("=== LLMModel.predict ===")
    print(f"Вопрос: {question}")
    print(f"Ответ:  {answer}\n")

    # 3) Эмбединг
    embedder = factory.get_embedding()
    snippets = ["Какого цвета трава?", "Зелёная трава"]
    vectors = embedder.embed(snippets)
    print("=== EmbeddingModel.embed ===")
    for text, vec in zip(snippets, vectors):
        print(f"{text!r} → {vec[:8]}…")  # показываем первые 8 значений

if __name__ == "__main__":
    main()
