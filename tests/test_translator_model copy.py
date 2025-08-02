from monitoring_dashboard import TranslatorModel

class DummyTranslator(TranslatorModel):
    def __init__(self):
        super().__init__("dummy-model")
    def predict(self, prompt: str, temperature: float = 0.0) -> str:
        # Эмулируем перевод по префиксу промта
        if prompt.startswith("Translate to English"):
            return "translated to english"
        if prompt.startswith("Переведи на русский"):
            return "переведено на русский"
        return ""

def test_translate_to_en():
    tr = DummyTranslator()
    out = tr.translate_to_en("текст на русском")
    assert out == "translated to english"

def test_translate_to_ru():
    tr = DummyTranslator()
    out = tr.translate_to_ru("some text")
    assert out == "переведено на русский"
