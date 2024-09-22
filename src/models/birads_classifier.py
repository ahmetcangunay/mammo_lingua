import spacy


class BiradsClassifier:

    def __init__(self, model: str):
        self.nlp = spacy.load(model)

    def get_classification(self, text):
        doc = self.nlp(text)
        estimated_cats = sorted(
            doc.cats.items(), key=lambda i: float(i[1]), reverse=True)
        estimated_cat = estimated_cats[0]
        return estimated_cat[0]
