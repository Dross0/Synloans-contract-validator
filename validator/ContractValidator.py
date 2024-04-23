from dto.MessageModel import Contract
from extractor.ContractModelExtractor import ContractModelExtractor
from deeppavlov import build_model
from dto.ContractModel import ContractModel
from comparator.Comparators import *
from comparator.ValidationResult import ValidationResult, ValidationError, ValidationWarning, ValidationFailure, InspectedObject
import enum


class ContractType(enum.Enum):
    LOAN_AGREEMENT = 'LOAN_AGREEMENT'

    SYNDICATE_AGREEMENT = 'SYNDICATE_AGREEMENT'

    ADDITIONAL_INFORMATION = 'ADDITIONAL_INFORMATION'

    LEGAL_CHARTER = 'LEGAL_CHARTER'

    FOUNDATION_AGREEMENT = 'FOUNDATION_AGREEMENT'

    TAX_STATEMENT = 'TAX_STATEMENT'

    REGISTER_EXTRACT = 'REGISTER_EXTRACT'

    @classmethod
    def from_str(cls, label: str):
        for k, v in cls.__members__.items():
            if k == label.upper() or v == label.upper():
                return v
        else:
            raise ValueError(f"'{cls.__name__}' enum not found for '{label}'")


class LoanAgreementValidator:

    def __init__(self):
        pass

    def validate(self, contract: Contract, model: ContractModel) -> ValidationResult:
        result = ValidationResult()

        participant_compare_result = identity_participant_compare(contract.loan_request, model.participants)
        result.add_result(participant_compare_result)

        rate_compare_result = compare_rate(contract.loan_request, model.rate)
        result.add_result(rate_compare_result)

        term_compare_result = compare_term(contract.loan_request, model.term)
        result.add_result(term_compare_result)

        loan_sum_compare_result = compare_loan_sum(contract.loan_request, model.money)
        result.add_result(loan_sum_compare_result)

        participant_money_compare_result = compare_participant_money(contract.loan_request, model.money)
        result.add_result(participant_money_compare_result)

        companies_inn_compare_result = compare_inn(contract.loan_request, model.inns)
        result.add_result(companies_inn_compare_result)

        companies_kpp_compare_result = compare_kpp(contract.loan_request, model.kpps)
        result.add_result(companies_kpp_compare_result)

        companies_ogrn_compare_result = compare_ogrn(contract.loan_request, model.ogrns, False)
        result.add_result(companies_ogrn_compare_result)

        return result


class SyndicateAgreementValidator:

    def __init__(self):
        pass

    def validate(self, contract: Contract, model: ContractModel) -> ValidationResult:
        result = ValidationResult()
        participant_compare_result = identity_participant_compare(contract.loan_request, model.participants)
        result.add_result(participant_compare_result)

        if model.rate is None and contract.loan_request.rate is not None:
            result.add_warning(InspectedObject.RATE, f"Rate from request={contract.loan_request.rate} not found at contract")
        else:
            rate_compare_result = compare_rate(contract.loan_request, model.rate)
            result.add_result(rate_compare_result)

        if model.term is None and contract.loan_request.term is not None:
            result.add_warning(InspectedObject.TERM, f"Term from request={contract.loan_request.term} not found at contract")
        else:
            term_compare_result = compare_term(contract.loan_request, model.term)
            result.add_result(term_compare_result)

        if model.money is None or not model.money:
            result.add_warning(InspectedObject.LOAN_SUM, f"Loan sum from request={contract.loan_request.sum} not found at contract")
            result.add_warning(InspectedObject.PARTICIPANT_MONEY, f'Participants money not found')
        else:
            money_compare_result = compare_loan_sum(contract.loan_request, model.money)
            participant_money_compare_result = compare_participant_money(contract.loan_request, model.money)
            result.add_result(money_compare_result)
            result.add_result(participant_money_compare_result)

        if model.inns is None or not model.inns:
            result.add_warning(InspectedObject.BORROWER_INN,
                               f"Borrower inn not found at contract")
            result.add_warning(InspectedObject.PARTICIPANT_INN, f'Participants inns not found')
        else:
            inn_compare_result = compare_inn(contract.loan_request, model.inns)
            result.add_result(inn_compare_result)

        if model.kpps is None or not model.kpps:
            result.add_warning(InspectedObject.BORROWER_KPP,
                               f"Borrower kpp not found at contract")
            result.add_warning(InspectedObject.PARTICIPANT_KPP, f'Participants kpps not found')
        else:
            kpp_compare_result = compare_kpp(contract.loan_request, model.kpps)
            result.add_result(kpp_compare_result)

        if model.ogrns is None or not model.ogrns:
            result.add_warning(InspectedObject.BORROWER_OGRN,
                               f"Borrower ogrn not found at contract")
            result.add_warning(InspectedObject.PARTICIPANT_OGRN, f'Participants ogrns not found')
        else:
            ogrn_compare_result = compare_ogrn(contract.loan_request, model.ogrns, False)
            result.add_result(ogrn_compare_result)

        return result


class ContractValidator:

    def __init__(self):
        self.__model_extractor = ContractModelExtractor(
            'ru_core_news_md',
            build_model('ner_rus_bert', download=False, install=False)
        )
        self.__validators = {
            ContractType.LOAN_AGREEMENT: LoanAgreementValidator(),
            ContractType.SYNDICATE_AGREEMENT: SyndicateAgreementValidator()
        }

    def validate(self, contract: Contract) -> ValidationResult:
        model = self.__model_extractor.extract_model(contract.content)
        try:
            contract_type = ContractType.from_str(contract.type.strip())
        except ValueError:
            return ValidationResult(ValidationError(InspectedObject.CONTRACT_TYPE, f"Contract has unknown type='{contract.type}'"))

        validator = self.__validators.get(contract_type)

        if validator is None:
            return ValidationResult(ValidationWarning(InspectedObject.CONTRACT_TYPE, f"Contract with type='{contract_type}' no need validation"))
        else:
            return validator.validate(contract, model)
