from app.kafka.client import KafkaClient 
from app.redis.redis import RedisClient
from app.htttp_client.client import HTTPClient
from app.controller.abstract import AbstractController
from fastapi import Request
from app.enum import TaskStatusesEnum
import json

class WebhookController(AbstractController):
    def __init__(self, kafka_client: KafkaClient, redis_client: RedisClient, http_client: HTTPClient):
        super().__init__(http_client)
        self._kafka_client = kafka_client
        self._redis_client = redis_client

    async def handle(self, request: Request):
        task_id = await self.extract_task_id_from_request(request)
        redis_note = json.loads(self._redis_client.get_note(f"task:{task_id}"))
        self._redis_client.update_task_status_with_outbox(task_id, TaskStatusesEnum.processed.value)
        payload = {
            "task_id": redis_note["task_id"],
            "user_id": redis_note["user_id"],
            "key": redis_note['object_key'],
            "original_filename": redis_note["object_key"],
            "status": TaskStatusesEnum.processed.value
        }
        await self._kafka_client.send_message(
            topic=self._kafka_client.preprocess_topic,
            message_payload=payload,
        )
    async def extract_object_key_from_request(self, request: Request):
        return json.loads(await request.body())['Records'][0]['s3']['object']['key']

    async def extract_task_id_from_request(self, request: Request):
        return json.loads(await request.body())['Records'][0]['s3']['object']['userMetadata']['x-amz-meta-task_id']