import dataclasses as dc
from decimal import Decimal
from extractor.TermModelExtractor import Term
from extractor.MoneyModelExtractor import Money


@dc.dataclass(frozen=True)
class ParticipantsModel:
    borrower: str
    syndicate_participants: [str]


@dc.dataclass(frozen=True)
class ContractModel:
    participants: ParticipantsModel
    rate: Decimal
    term: Term
    money: [Money]
    inns: [str]
    kpps: [str]
    ogrns: [str]
