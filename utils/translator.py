import deep_translator

class Translator:
    def __init__(self):
        self.google = deep_translator.GoogleTranslator

    def translate(self, text, engine="google", source="auto", target="en"):
        if engine == "google":
            return self.google(source=source, target=target).translate(text)
        else:
            raise ValueError("Unknown engine")