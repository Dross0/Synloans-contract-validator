import enum


class InspectedObject(enum.Enum):
    BORROWER = 'borrower'

    BORROWER_INN = 'borrower inn'

    BORROWER_KPP = 'borrower kpp'

    BORROWER_OGRN = 'borrower ogrn'

    PARTICIPANT = 'syndicate participant'

    PARTICIPANT_INN = 'syndicate participant inn'

    PARTICIPANT_KPP = 'syndicate participant kpp'

    PARTICIPANT_OGRN = 'syndicate participant ogrn'

    SYNDICATE_PARTICIPANTS = 'syndicate participants'

    RATE = 'rate'

    LOAN_SUM = 'loan sum'

    PARTICIPANT_MONEY = 'participant money'

    TERM = 'term'

    CONTRACT_TYPE = 'contract type'

    @classmethod
    def from_str(cls, label: str):
        for k, v in cls.__members__.items():
            if k == label.upper() or v == label.upper():
                return v
        else:
            raise ValueError(f"'{cls.__name__}' enum not found for '{label}'")


class ValidationFailure:
    def __init__(self, inspected_object: InspectedObject, message: str, critical: bool):
        self._message = message
        self._inspected_object = inspected_object
        self._critical = critical

    def get_message(self) -> str:
        return self._message

    def get_inspected_object(self) -> InspectedObject:
        return self._inspected_object

    def is_critical(self) -> bool:
        return self._critical

    def __str__(self):
        return f"Failure(critical={self._critical}, inspected_object = {self._inspected_object}, message={self._message})"


class ValidationError(ValidationFailure):
    def __init__(self, inspected_object: InspectedObject, message: str):
        super().__init__(inspected_object, message, True)

    def __str__(self):
        return f"Error(inspected_object = {self._inspected_object}, message={self._message})"


class ValidationWarning(ValidationFailure):
    def __init__(self, inspected_object: InspectedObject, message: str):
        super().__init__(inspected_object, message, False)

    def __str__(self):
        return f"Warning(inspected_object = {self._inspected_object}, message={self._message})"


class ValidationResult:
    def __init__(self, validation_failure: ValidationFailure = None):
        self.__validation_failures = []
        if validation_failure is not None:
            self.__validation_failures.append(validation_failure)

    def add_error(self, inspected_object: InspectedObject, message: str):
        self.__validation_failures.append(ValidationError(inspected_object, message))

    def add_warning(self, inspected_object:InspectedObject, message: str):
        self.__validation_failures.append(ValidationWarning(inspected_object, message))

    def add_result(self, validation_result):
        for error in list(validation_result.get_validation_failures()):
            self.__validation_failures.append(error)

    def is_success(self):
        return all([not error.is_critical() for error in self.__validation_failures])

    def get_validation_failures(self):
        return self.__validation_failures

    def __str__(self):
        failures = [str(failure) for failure in self.__validation_failures]
        if self.is_success():
            return "Success validation result. Warnings=\n" + '\n'.join(failures)
        else:
            return "Failed validation result. Failures=\n" + '\n'.join(failures)
