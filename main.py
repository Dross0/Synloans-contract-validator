from service import ValidationService, ValidationResultSender, ValidationConsumer

result_topic = 'CONTRACTVALIDATIONRESULT.V1'
request_topic = 'CONTRACTVALIDATION.V1'

bootstrap_servers = 'localhost:9092'

consumer_group_id = 'contract-validator'


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    validation_service = ValidationService()

    result_sender = ValidationResultSender(result_topic,bootstrap_servers)

    consumer = ValidationConsumer(
        validation_service,
        result_sender,
        request_topic,
        bootstrap_servers,
        consumer_group_id
    )

    consumer.run()