import json
from app.config import KafkaConfig
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer


class KafkaClient:
    def __init__(
        self,
        config: KafkaConfig,
        producer: AIOKafkaProducer,
    ) -> None:
        self._config = config
        self._producer = producer

    async def send_message(self, topic: str, message_payload: dict) -> str:
        """Отправляет сообщение в очередь."""
        await self._producer.send(
            topic=topic, value=json.dumps(message_payload).encode('utf-8')
        )

    @property
    def preprocess_topic(self):
        return self._config.preprocess_topic

    @property
    def outbox_topic(self):
        return self._config.outbox_topic
