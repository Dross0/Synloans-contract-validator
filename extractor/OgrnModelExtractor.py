import re


class OgrnModelExtractor:
    pattern = r'\s+\d{13}\s+'

    def __init__(self, nlp):
        self.__nlp = nlp

    def extract(self, content: str) -> [str]:
        ogrn_list = []
        all_ogrns = re.findall(self.pattern, content)
        for match in all_ogrns:
            ogrn = self.__resolve_ogrn(match)
            ogrn_list.append(ogrn)

        return ogrn_list

    def __resolve_ogrn(self, ogrn_match: str):
        return ogrn_match.strip()
