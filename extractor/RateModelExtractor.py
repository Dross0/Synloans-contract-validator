from utils.TextUtils import find_distance
import re
from decimal import Decimal


class RateModelExtractor:
    pattern = r'(\d+(?:\.\d+)?)\s*%'

    keyword_weights = {
        "процент": 4,
        "ставка": 5,
        "годовых": 5,
        "год": 2,
        "процентов": 4,
        "процентный": 3,
        "годовая": 3,
    }

    def __init__(self, nlp):
        self.__nlp = nlp

    def extract(self, content: str) -> Decimal:
        doc = self.__nlp(content)
        interest_rates = {}
        for sent in doc.sents:
            interest_rate_score = self.__get_sent_interest_rate(sent)
            if interest_rate_score is not None:
                interest_rates[interest_rate_score[0]] = max(
                    interest_rate_score[1],
                    interest_rates.get(interest_rate_score[0], 0)
                )
        return Decimal(max(interest_rates.items(), key=lambda k: k[1])[0])

    def __get_sent_interest_rate(self, sent):
        sent_rates = self.__extract_interest_rates_regex(sent.text)
        if len(sent_rates) == 0:
            return None
        max_score = -1
        max_rate = ""
        for rate in sent_rates:
            score = 0
            for keyword in self.keyword_weights:
                dist = find_distance(self.__nlp, sent, keyword, rate)
                if dist != -1:
                    score += (1 / dist) * self.keyword_weights[keyword]
            if score > max_score:
                max_score = score
                max_rate = rate
        return Decimal(re.match(self.pattern, max_rate).group(1)), max_score

    def __extract_interest_rates_regex(self, content):
        matches = re.finditer(self.pattern, content)
        return [match.group(0) for match in matches]