import re


class InnModelExtractor:
    pattern = r'\s+\d{10}\s+'

    def __init__(self, nlp):
        self.__nlp = nlp

    def extract(self, content: str) -> [str]:
        inn_list = []
        all_inns = re.findall(self.pattern, content)
        for match in all_inns:
            inn = self.__resolve_inn(match)
            inn_list.append(inn)

        return inn_list

    def __resolve_inn(self, inn_match: str):
        return inn_match.strip()
