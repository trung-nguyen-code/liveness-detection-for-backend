import fasttext


class LanguageIdentification:
    def __init__(self):
        pretrained_lang_model = "models/lid.176.bin"
        self.model = fasttext.load_model(pretrained_lang_model)

    def predict_lang(self, text):
        predictions = self.model.predict(text, k=1)  # returns top 2 matching languages
        return predictions
