from pprint import pprint


from comparator.ValidationResult import ValidationFailure
from validator.ContractValidator import ContractValidator
from datetime import date
from decimal import Decimal
from dto.MessageModel import LoanRequest, Contract, CompanyInfo, SyndicateParticipant

with open('synData.txt', 'r') as file:
    content = file.read()

validator = ContractValidator()

contract = Contract(
    1,
    content,
    'LOAN_AGREEMENT',
    LoanRequest(
        Decimal(10_250_000),
        60,
        Decimal("10.2"),
        date(2024, 4, 1),
        CompanyInfo(
            "XYZ Inc",
            "Газпром",
            "1234567890",
            "987654321",
            "Москва, ул Иванова, д 2",
            "Москва, ул Иванова, д 2",
            "1029384756111",
            "98765",
            "485022"
        ),
        [
            SyndicateParticipant(
                CompanyInfo(
                    "ОАО ВТБ",
                    "ВТБ",
                    "9876678900",
                    "111222333",
                    "Москва, ул Ленина, д 2",
                    "Москва, ул Ленина, д 2",
                    None,
                    "98765",
                    "485022"
                ),
                Decimal(2_800_000),
                False
            ),
            SyndicateParticipant(
                CompanyInfo(
                    "ПАО Сбербанк",
                    "Сбер",
                    "7788223344",
                    "888899999",
                    "Москва, ул Вавилова, д 2",
                    "Москва, ул Вавилова, д 2",
                    "0001112223334",
                    "98765",
                    "485022"
                ),
                Decimal(7_200_000),
                True
            )
        ]
    )
)

validation_result = validator.validate(contract)
print(validation_result)


def __to_failure(failure: ValidationFailure) -> dict:
    return {
        "critical": failure.is_critical(),
        "inspectedObject": failure.get_inspected_object().name,
        "message": failure.get_message()
    }

pprint({
                'contractId': contract.id,
                'valid': validation_result.is_success(),
                'errors': [__to_failure(failure) for failure in validation_result.get_validation_failures()]
            }
)
