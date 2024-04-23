import spacy

from dto.ContractModel import ContractModel
from extractor.MoneyModelExtractor import MoneyModelExtractor
from extractor.ParticipantModelExtractor import ParticipantModelExtractor
from extractor.RateModelExtractor import RateModelExtractor
from extractor.InnModelExtractor import InnModelExtractor
from extractor.KppModelExtractor import KppModelExtractor
from extractor.OgrnModelExtractor import OgrnModelExtractor
from extractor.TermModelExtractor import TermModelExtractor
from preprocessor import StopWordRemoverPreprocessor


class ContractModelExtractor:

    def __init__(self, nlp_set, ner_model):
        self.__nlp = spacy.load(nlp_set)
        self.__ner_model = ner_model
        self.__participant_extractor = ParticipantModelExtractor(self.__nlp, ner_model)
        self.__rate_extractor = RateModelExtractor(self.__nlp)
        self.__term_extractor = TermModelExtractor(self.__nlp)
        self.__money_extractor = MoneyModelExtractor(self.__nlp)
        self.__inn_extractor = InnModelExtractor(self.__nlp)
        self.__kpp_extractor = KppModelExtractor(self.__nlp)
        self.__ogrn_extractor = OgrnModelExtractor(self.__nlp)
        self.__preprocessors = [
            StopWordRemoverPreprocessor(self.__nlp)
            # LemmatizationPreprocessor(self.nlp)
        ]

    def __preprocess(self, content: str) -> str:
        preprocessed_content = content
        for preprocessor in self.__preprocessors:
            preprocessed_content = preprocessor.preprocess(preprocessed_content)
        return preprocessed_content

    def extract_model(self, content: str):
        preprocessed_content = self.__preprocess(content)
        rate = self.__rate_extractor.extract(preprocessed_content)
        participants_model = self.__participant_extractor.extract(preprocessed_content)
        term = self.__term_extractor.extract(preprocessed_content)
        money = self.__money_extractor.extract(preprocessed_content)
        inns = self.__inn_extractor.extract(preprocessed_content)
        kpps = self.__kpp_extractor.extract(preprocessed_content)
        ogrns = self.__ogrn_extractor.extract(preprocessed_content)
        contract_model = ContractModel(
            participants_model,
            rate,
            term,
            money,
            inns,
            kpps,
            ogrns
        )
        print(contract_model)
        return contract_model
