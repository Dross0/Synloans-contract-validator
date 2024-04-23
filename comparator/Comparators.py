from typing import Optional

from dto.MessageModel import LoanRequest, CompanyInfo
from dto.ContractModel import ParticipantsModel
from decimal import *
from comparator.ValidationResult import *
from extractor.TermModelExtractor import Term, TermUnit
from extractor.MoneyModelExtractor import Money, MoneyUnit

rate_epsilon = Decimal('0.001')

def compare_str(str1: str, str2: str) -> bool:
    if str1 is None and str2 is None:
        return True
    elif str1 is None or str2 is None:
        return False
    else:
        return str1.strip().lower() == str2.strip().lower()


def is_empty(check_str: str) -> bool:
    return check_str is None or check_str.strip() == ""


def identity_compare_company_name(company: CompanyInfo, checked_name: str, role: InspectedObject) -> ValidationResult:
    result = ValidationResult()
    if compare_str(company.full_name, checked_name):
        return result

    result.add_warning(role,
                       f"Company with role={role} full names not equal. Expected='{company.full_name}', actual='{checked_name}'")

    if compare_str(company.short_name, checked_name):
        return result

    result.add_warning(role,
                       f"Company with role={role} short names not equal. Expected='{company.short_name}', actual='{checked_name}'")
    result.add_error(role, f'Company wit role={role} names not equal')

    return result


def find_participant(participant: CompanyInfo, participant_model: ParticipantsModel) -> (str, ValidationResult):
    for model_participant_name in participant_model.syndicate_participants:
        result = identity_compare_company_name(
            participant,
            model_participant_name,
            InspectedObject.PARTICIPANT
        )
        if result.is_success():
            return model_participant_name, result
    return None


def identity_participant_compare(loan_request: LoanRequest, participant_model: ParticipantsModel) -> ValidationResult:
    result = ValidationResult()
    if is_empty(participant_model.borrower):
        result.add_error(InspectedObject.BORROWER, 'Empty borrower at model')
    else:
        compare_borrower_name_result = identity_compare_company_name(
            loan_request.borrower,
            participant_model.borrower,
            InspectedObject.BORROWER
        )
        result.add_result(compare_borrower_name_result)

    found_participants_count = len(participant_model.syndicate_participants)
    loan_request_participants_count = len(loan_request.syndicate_participants)

    if not participant_model.syndicate_participants:
        result.add_error(InspectedObject.SYNDICATE_PARTICIPANTS, 'Empty syndicate participants at model')
        return result
    elif found_participants_count > loan_request_participants_count:
        result.add_warning(InspectedObject.SYNDICATE_PARTICIPANTS, f"Found more organizations than participants. Found organizations={found_participants_count}, excepted participants={loan_request_participants_count}")
    elif found_participants_count < loan_request_participants_count:
        result.add_warning(InspectedObject.SYNDICATE_PARTICIPANTS,
                           f"Found less organizations than participants. Found organizations={found_participants_count}, excepted participants={loan_request_participants_count}")

    checked_participants_count = min(loan_request_participants_count, found_participants_count)
    visited_participants = set()
    for participant in loan_request.syndicate_participants[:checked_participants_count]:
        participant_result = find_participant(participant.bank, participant_model)
        if participant_result is None:
            result.add_error(InspectedObject.PARTICIPANT,
                             f"Syndicate participant '{participant.bank.full_name}' not found at model participant list.")
        else:
            visited_participants.add(participant_result[0])
            result.add_result(participant_result[1])

    unexpected_model_participants = set(participant_model.syndicate_participants) - visited_participants

    for unexpected_model_participant in unexpected_model_participants:
        for participant in loan_request.syndicate_participants:
            participant_result = find_participant(participant.bank, participant_model)
            if participant_result is None:
                result.add_error(InspectedObject.SYNDICATE_PARTICIPANTS,
                                 f"Unexpected syndicate participant='{unexpected_model_participant}' at model")
    return result


def compare_rate(loan_request: LoanRequest, rate: Decimal) -> ValidationResult:
    getcontext().prec = 3
    result = ValidationResult()
    expected_rate = Decimal(loan_request.rate)
    if abs(expected_rate-rate) > rate_epsilon:
        result.add_error(InspectedObject.RATE, f'Rates are not same. Expected={expected_rate}, actual={rate}')
    return result


def compare_loan_sum(loan_request: LoanRequest, money: [Money]) -> ValidationResult:
    getcontext().prec = 3
    result = ValidationResult()
    expected_sum = Decimal(loan_request.sum)
    money_amount = [m.get_amount() for m in money]
    if expected_sum not in money_amount:
        result.add_error(InspectedObject.LOAN_SUM, f'Loan sums are not found. Expected={expected_sum}')
    return result


def compare_participant_money(loan_request: LoanRequest, money: [Money]) -> ValidationResult:
    getcontext().prec = 3
    result = ValidationResult()
    money_amount = [m.get_amount() for m in money]
    for participant in loan_request.syndicate_participants:
        participant_sum = Decimal(participant.sum)
        if participant_sum not in money_amount:
            result.add_error(InspectedObject.PARTICIPANT_MONEY,
                             f'Money of participant="{participant.bank.full_name}" not found. Expected={participant_sum}')
    return result


def convert_term_to_months(term: Term) -> int:
    if term.unit == TermUnit.DAY:
        return term.term // 30
    elif term.unit == TermUnit.WEEK:
        return term.term // 4
    elif term.unit == TermUnit.MONTH:
        return term.term
    elif term.unit == TermUnit.YEAR:
        return term.term * 12
    return 0


def compare_term(loan_request: LoanRequest, term: Term) -> ValidationResult:
    getcontext().prec = 3
    result = ValidationResult()
    if term is None:
        result.add_error(InspectedObject.TERM, f'Model term not found')
        return result
    months_term = convert_term_to_months(term)
    if loan_request.term != months_term:
        result.add_error(InspectedObject.TERM,
                         f'Terms are not same. Expected={loan_request.term} months, actual={term}')
    return result


def compare_inn(loan_request: LoanRequest, inns: [str]) -> ValidationResult:
    result = ValidationResult()

    if loan_request.borrower.inn not in inns:
        result.add_error(InspectedObject.BORROWER_INN,
                         f'Inn of borrower="{loan_request.borrower.full_name}" not found. Expected={loan_request.borrower.inn}')

    for participant in loan_request.syndicate_participants:
        if participant.bank.inn not in inns:
            result.add_error(InspectedObject.PARTICIPANT_INN,
                             f'Inn of participant="{participant.bank.full_name}" not found. Expected={participant.bank.inn}')

    return result


def compare_kpp(loan_request: LoanRequest, kpps: [str]) -> ValidationResult:
    result = ValidationResult()
    if loan_request.borrower.kpp not in kpps:
        result.add_error(InspectedObject.BORROWER_KPP,
                         f'Kpp of borrower="{loan_request.borrower.full_name}" not found. Expected={loan_request.borrower.kpp}')

    for participant in loan_request.syndicate_participants:
        if participant.bank.kpp not in kpps:
            result.add_error(InspectedObject.PARTICIPANT_KPP,
                             f'Kpp of participant="{participant.bank.full_name}" not found. Expected={participant.bank.kpp}')

    return result


def add_failure_with_empty(result, inspected_object: InspectedObject, message: str, error_on_empty: bool = True):
    if error_on_empty:
        return result.add_error(inspected_object, message)
    else:
        return result.add_warning(inspected_object, message)

def compare_ogrn(loan_request: LoanRequest, ogrns: [str], error_on_empty: bool = True) -> ValidationResult:
    result = ValidationResult()
    if loan_request.borrower.ogrn is None:
        add_failure_with_empty(result, InspectedObject.BORROWER_OGRN, f'Empty ogrn of borrower', error_on_empty)
    elif loan_request.borrower.ogrn not in ogrns:
        result.add_error(InspectedObject.BORROWER_OGRN,
                         f'Ogrn of borrower="{loan_request.borrower.full_name}" not found. Expected={loan_request.borrower.ogrn}')

    for participant in loan_request.syndicate_participants:
        if participant.bank.ogrn is None:
            add_failure_with_empty(result, InspectedObject.PARTICIPANT_OGRN, f'Empty ogrn of participant={participant.bank.full_name}', error_on_empty)
        elif participant.bank.ogrn not in ogrns:
            result.add_error(InspectedObject.PARTICIPANT_OGRN,
                             f'Ogrn of participant="{participant.bank.full_name}" not found. Expected={participant.bank.ogrn}')

    return result

