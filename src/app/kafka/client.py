import asyncio
import json

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, ConsumerRecord

from src.app.s3.client.client import S3Client


class KafkaClient:
    
    def __init__(
            self,
            consumer: AIOKafkaConsumer,
            s3_client: S3Client,
            producer: AIOKafkaProducer,
        ):
        self._consumer = consumer
        self._s3_client = s3_client
        self._producer = producer
    
    async def process_message(self, message: ConsumerRecord):
        payload = json.loads(message.value.decode())
        await self._s3_client.get_object(key = payload['file_key'])
        return 'output.pdf'

    async def process_queue(self,):
        async for message in self._consumer:
            return await asyncio.create_task(self.process_message(message))