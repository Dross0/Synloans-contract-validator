from preprocessor.Preprocessor import Preprocessor


class StopWordRemoverPreprocessor(Preprocessor):

    def __init__(self, nlp):
        super().__init__()
        self.__nlp = nlp

    def preprocess(self, content: str) -> str:
        doc = self.__nlp(content)

        tokens_without_stopwords = [token.text for token in doc if not token.is_stop]

        clean_content = ' '.join(tokens_without_stopwords)

        return clean_content
