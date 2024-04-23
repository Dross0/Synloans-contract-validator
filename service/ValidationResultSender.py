from kafka import KafkaProducer
from json import dumps
from MessageConverter import *
from comparator.ValidationResult import ValidationResult, ValidationFailure

class ValidationResultSender:

    def __init__(self, topic, servers):
        self.__topic = topic
        self.__producer = KafkaProducer(
            bootstrap_servers=servers,
            value_serializer=lambda m: dumps(m).encode('ascii')
        )

    @staticmethod
    def __to_failure(failure: ValidationFailure) -> dict:
        return {
            "critical": failure.is_critical(),
            "inspectedObject": failure.get_inspected_object().name,
            "message": failure.get_message()
        }

    def send_result(self, contract: Contract, validation_result: ValidationResult):
        self.__producer.send(
            self.__topic,
            {
                'contractId': contract.id,
                'valid': validation_result.is_success(),
                'errors': [ValidationResultSender.__to_failure(failure) for failure in validation_result.get_validation_failures()]
            }
        )