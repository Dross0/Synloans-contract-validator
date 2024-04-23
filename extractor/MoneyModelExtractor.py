import re
from re import Match
from decimal import Decimal

import enum
import dataclasses as dc


class MoneyUnit(enum.Enum):
    ONE = 1
    THOUSAND = 1000
    MILLION = 1_000_000
    BILLION = 1_000_000_000

    @staticmethod
    def order():
        return [MoneyUnit.ONE, MoneyUnit.THOUSAND, MoneyUnit.MILLION, MoneyUnit.BILLION]


@dc.dataclass(frozen=True)
class Money:
    value: Decimal
    unit: MoneyUnit

    def get_amount(self) -> Decimal:
        if self.unit == MoneyUnit.ONE:
            return self.value
        sign, digits, exponent = self.value.as_tuple()
        if exponent == 0:
            number = int(''.join(map(str, digits)))
            return Decimal(number * self.unit.value)
        integer_part = int(''.join(map(str, digits[:exponent])))
        fractional_part = int(''.join(map(str, digits[exponent:])))
        return Decimal(integer_part * self.unit.value + fractional_part * self.unit.value // 10 ** -exponent)


class MoneyModelExtractor:
    pattern = r'([1-9]\d*(?:[ ,]\d{3})*(?:[.]\d+)?|\d+(?:[.]\d+)?)\s*(?:\([^)]*?\))??\s*((?:млрд\.?|млн\.?|тыс\.?)|(?:миллиард(?:а|ов)?|миллион(?:а|ов)?|тысяч(?:а|и|у|ей)?))?\s*(?:\([^)]*?\))??\s*(?:российских)?\s*(?:р(?:уб(?:ль|ля|лей|\.?|\b)?)|\u20BD)'

    money_units = {
        MoneyUnit.ONE: [""],
        MoneyUnit.THOUSAND: ["тыс", "тысяч", "тысяча", "тысячи", "тысячу", "тысячей"],
        MoneyUnit.MILLION: ["млн", "миллион", "миллионов", "миллиона"],
        MoneyUnit.BILLION: ["млрд", "миллиард", "миллиардов", "миллиарда"],
    }

    def __init__(self, nlp):
        self.__nlp = nlp

    def extract(self, content: str) -> [Money]:
        money_list = []
        all_money_matches = re.finditer(self.pattern, content)
        for match in all_money_matches:
            money = self.__resolve_money(match)
            money_list.append(money)

        return money_list

    def __resolve_money(self, money_match: Match):
        money_value_str = money_match.group(1)
        money_unit_str = money_match.group(2)

        money = Money(self.__convert_money_value(money_value_str), self.__convert_money_unit(money_unit_str))

        return money

    def __convert_money_value(self, money_value: str) -> Decimal:
        money_value = money_value.strip().replace(' ', '').replace(',', '')
        return Decimal(money_value)

    def __convert_money_unit(self, money_unit_str: str) -> MoneyUnit:
        if money_unit_str is None:
            return MoneyUnit.ONE
        money_unit_str = money_unit_str.strip().replace('.', '')
        for money_unit in self.money_units:
            if money_unit_str in self.money_units[money_unit]:
                return money_unit
        return MoneyUnit.ONE
