import asyncio
import json

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, ConsumerRecord

from app.s3.client.client import S3Client


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
        await self._s3_client.get_object(payload['file_key'])
        await self._s3_client.upload_file(output_pdf)
        await self._producer.send(
            'last-topic',
            json.dumps(
                {
                    "status": "complete",
                    "file_key": output_pdf,
                }
            ).encode('utf-8')
        )

    async def process_queue(self,):
        async for message in self._consumer:
            asyncio.create_task(self.process_message(message))