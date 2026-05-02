from app.redis.redis import RedisClient
from app.kafka.client import KafkaClient
import json
import asyncio


class OutboxManager:
    """Имплементация паттерна Outbox для атомарности операции отправки сообщения и записи в брокер."""

    def __init__(self, redis_client: RedisClient, kafka_client: KafkaClient):
        self._redis_client = redis_client
        self._kafka_client = kafka_client

    async def run(
        self,
    ):
        while True:
            event_json = self._redis_client._redis.rpoplpush(
                "outbox", "outbox:processing", timeout=1
            )
            if event_json is None:
                continue
            event = json.loads(event_json)
            try:
                await self._kafka_client._producer.send(self.topic, value=event)
                self._redis_client._redis.lrem("outbox:processing", 1, event_json)
                print(f"Published event {event['event_id']}")
            except Exception as e:
                print(f"Failed to publish {event['event_id']}: {e}")
                self._redis_client._redis.rpush("outbox", event_json)
                self._redis_client._redis.lrem("outbox:processing", 1, event_json)
                asyncio.sleep(5)
