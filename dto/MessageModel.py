import dataclasses as dc
from datetime import date
from decimal import Decimal

@dc.dataclass(frozen=True)
class CompanyInfo:
    full_name: str
    short_name: str
    inn: str
    kpp: str
    legal_address: str
    actual_address: str
    ogrn: str
    okpo: str
    okato: str


@dc.dataclass(frozen=True)
class SyndicateParticipant:
    bank: CompanyInfo
    sum: Decimal
    approve_bank_agent: bool


@dc.dataclass(frozen=True)
class LoanRequest:
    sum: Decimal
    term: int
    rate: Decimal
    create_date: date
    borrower: CompanyInfo
    syndicate_participants: list[SyndicateParticipant]


@dc.dataclass(frozen=True)
class Contract:
    id: int
    content: str
    type: str
    loan_request: LoanRequest
