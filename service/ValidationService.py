from comparator.ValidationResult import ValidationResult
from dto.MessageModel import Contract
from validator.ContractValidator import ContractValidator


class ValidationService:

    def __init__(self):
        self.__contract_validator = ContractValidator()

    def validate(self, contract: Contract) -> ValidationResult:
        return self.__contract_validator.validate(contract)

