from preprocessor.Preprocessor import Preprocessor


class LemmatizationPreprocessor(Preprocessor):

    def __init__(self, nlp):
        super().__init__()
        self.__nlp = nlp

    def preprocess(self, content: str) -> str:
        doc = self.__nlp(content)

        lemmatized_tokens = [token.lemma_ for token in doc]

        lemmatized_text = ' '.join(lemmatized_tokens)

        return lemmatized_text
