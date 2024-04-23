from typing import Optional
from utils.TextUtils import find_distance_index
from utils.TextUtils import find_distance_index
import re

import enum
import dataclasses as dc


class TermUnit(enum.Enum):
    DAY = 1
    WEEK = 2
    MONTH = 3
    YEAR = 4


@dc.dataclass(frozen=True)
class Term:
    term: int
    unit: TermUnit


class TermModelExtractor:
    max_unit_distance = 5
    day_unit_keywords = ['день', 'дня', 'дней']
    week_unit_keywords = ['неделя', 'недели', 'недель']
    month_unit_keywords = ['месяц', 'месяца', 'месяцев']
    year_unit_keywords = ['год', 'года', 'лет']
    term_keywords = ['срок', 'длительность', 'период']

    def __init__(self, nlp):
        self.__nlp = nlp

    def extract(self, content: str):
        doc = self.__nlp(content)
        terms = {}
        for sent in doc.sents:
            for idx, token in enumerate(sent):
                if token.is_digit:
                    term_token = sent[idx]
                    unit_idx = idx + 1
                    unit_token = sent[unit_idx]

                    skipped = 0
                    while unit_idx + 1 < len(sent) and skipped <= self.max_unit_distance and self.__get_term_unit(unit_token.lower_) is None:
                        unit_idx += 1
                        skipped += 1
                        unit_token = sent[unit_idx]
                    term = self.__build_term(term_token, unit_token.lower_)
                    if term is not None:
                        relative_score = self.__count_relative_score(self.__nlp, sent, term_token.idx - sent.start_char,
                                                                     unit_token.idx + len(unit_token) - sent.start_char)
                        terms[term] = terms.get(term, 0) + relative_score
        if not terms:
            return None
        return max(terms.items(), key=lambda k: k[1])[0]

    def __count_relative_score(self, nlp, sentence, term_start_index, term_end_index):
        count = 0
        score = 0.0
        for keyword in self.term_keywords:
            dist = find_distance_index(nlp, sentence, keyword, term_start_index, term_end_index)
            if dist != -1:
                count += 1
                score += 1 / dist
        return score * count

    def __get_term_unit(self, term_unit_token) -> Optional[TermUnit]:
        if term_unit_token in self.day_unit_keywords:
            return TermUnit.DAY
        elif term_unit_token in self.week_unit_keywords:
            return TermUnit.WEEK
        elif term_unit_token in self.month_unit_keywords:
            return TermUnit.MONTH
        elif term_unit_token in self.year_unit_keywords:
            return TermUnit.YEAR
        return None

    def __build_term(self, term_value_token, term_unit_token) -> Optional[Term]:
        try:
            term_unit = self.__get_term_unit(term_unit_token)
            if term_unit is None:
                return None
            term_value = int(term_value_token.lower_)
            return Term(term_value, term_unit)
        except ValueError:
            return None
