from kafka import KafkaConsumer
from json import loads
from MessageConverter import *
from service import ValidationService, ValidationResultSender

class ValidationConsumer:

    def __init__(
            self,
            validation_service: ValidationService,
            validation_result_sender: ValidationResultSender,
            topic: str,
            servers: str,
            group_id: str
    ):
        self.__consumer = KafkaConsumer(
            topic,
            bootstrap_servers=servers,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=group_id,
            value_deserializer=lambda x: loads(x.decode('utf-8'))
        )
        self.__validation_service = validation_service
        self.__validation_result_sender = validation_result_sender

    def run(self):
        for msg in self.__consumer:
            contract = build_contract(msg.value)
            print(contract)

            validation_result = self.__validation_service.validate(contract)

            print(validation_result)

            self.__validation_result_sender.send_result(contract, validation_result)