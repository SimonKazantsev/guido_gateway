import json
from app.config import KafkaConfig
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer


class KafkaClient:
    def __init__(
        self,
        config: KafkaConfig,
    ) -> None:
        self._config = config
        self._consumer = AIOKafkaConsumer(bootstrap_servers=config.bootstrap_servers)
        self._producer = AIOKafkaProducer(bootstrap_servers=config.bootstrap_servers)

    async def send_message(self, message_payload: dict) -> str:
        """Отправляет сообщение в очередь."""
        await self._producer.send(
            topic=self._config.process_link_topic, value=json.dumps(message_payload)
        )

    @property
    def process_link_topic(self):
        return self._config.process_link_topic

    @property
    def outbox_topic(self):
        return self._config.outbox_topic
