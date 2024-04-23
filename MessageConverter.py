import datetime

from dto.MessageModel import LoanRequest, Contract, CompanyInfo, SyndicateParticipant
from decimal import Decimal

def build_company_info(c) -> CompanyInfo:
    return CompanyInfo(
        c['fullName'],
        c['shortName'],
        c['inn'],
        c['kpp'],
        c['legalAddress'],
        c['actualAddress'],
        c['ogrn'],
        c['okpo'],
        c['okato']
    )


def build_syndicate_participant(sp) -> SyndicateParticipant:
    return SyndicateParticipant(
        build_company_info(sp['bank']),
        Decimal(sp['sum']),
        sp['approveBankAgent']
    )


def build_loan_request(lr) -> LoanRequest:
    participants = []
    if lr['syndicateParticipants'] is not None:
        participants = [build_syndicate_participant(sp) for sp in lr['syndicateParticipants']]

    raw_date = lr['createDate']
    return LoanRequest(
        Decimal(lr['sum']),
        lr['term'],
        Decimal(lr['rate']),
        datetime.date(raw_date[0], raw_date[1], raw_date[2]),
        build_company_info(lr['borrower']),
        participants
    )


def build_contract(msg) -> Contract:
    return Contract(
        msg['contractId'],
        msg['contractText'],
        msg['contractType'],
        build_loan_request(msg['loanRequest'])
    )
