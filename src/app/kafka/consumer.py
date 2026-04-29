from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.s3.client.client import S3Client

KAFKA_TOPIC = "kafka_topic"


class KafkaClient:
    def __init__(
        self,
        consumer: AIOKafkaConsumer,
        s3_client: S3Client,
        producer: AIOKafkaProducer,
    ) -> None:
        self._consumer = consumer
        self._s3_client = s3_client
        self._producer = producer

    async def send_message(self, message_payload: dict):
        await self._producer.send(
            topic=KAFKA_TOPIC, headers=message_payload["task_id"], value=message_payload
        )
