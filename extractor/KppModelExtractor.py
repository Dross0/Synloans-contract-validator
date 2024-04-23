import re


class KppModelExtractor:
    pattern = r'\s+\d{9}\s+'

    def __init__(self, nlp):
        self.__nlp = nlp

    def extract(self, content: str) -> [str]:
        kpp_list = []
        all_kpps = re.findall(self.pattern, content)
        for match in all_kpps:
            kpp = self.__resolve_kpp(match)
            kpp_list.append(kpp)

        return kpp_list

    def __resolve_kpp(self, kpp_match: str):
        return kpp_match.strip()
