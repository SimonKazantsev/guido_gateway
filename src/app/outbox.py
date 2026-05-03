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
        self._recover_processing()
        while True:
            event_json = self._redis_client._redis.rpoplpush(
                self._kafka_client.outbox_topic, "outbox:processing", timeout=1
            )
            if event_json is None:
                await asyncio.sleep(0.1)
                continue

            event = json.loads(event_json)
            try:
                await self._kafka_client._producer.send(self._kafka_client.outbox_topic, value=event)
                self._redis_client._redis.lrem("outbox:processing", 1, event_json)
                print(f"Published event {event['event_id']}")
            except Exception as e:
                print(f"Failed to publish {event['event_id']}: {e}")
                self._redis_client._redis.rpush("outbox", event_json)
                self._redis_client._redis.lrem("outbox:processing", 1, event_json)
                await asyncio.sleep(5)
    
    def _recover_processing(self,):
        """Перенести все сообщения из outbox:processing обратно в outbox при старте."""
        while True:
            event_json = self._redis_client._redis.rpoplpush("outbox:processing", "outbox", timeout=0)
            if not event_json:
                break
            print(f"Recovered orphaned event from processing: {event_json}")
