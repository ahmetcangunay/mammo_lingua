import spacy


class NerModel:

    def __init__(self, model: str):
        self.nlp = spacy.load(model)

    def get_entities(self, text):
        doc = self.nlp(text)

        colors = {"ANAT": "#A020F0",
                  "OBS-PRESENT": "#30D5C8",
                  "OBS-ABSENT": "#FFFF00",
                  "OBS-UNCERTAIN": "#808080",
                  "IMPRESSION": "#FF0000"}
        options = {"colors": colors}
        return doc, options
