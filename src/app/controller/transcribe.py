from app.controller.abstract import AbstractController
from fastapi.responses import JSONResponse
from fastapi import Request, Response
from pydantic import BaseModel, HttpUrl
import uuid
from app.enum import TaskStatusesEnum
from app.redis.redis import RedisClient
from app.kafka.client import KafkaClient
from app.s3.client.client import S3Client


class ProcessLinkRequest(BaseModel):
    url: HttpUrl
    user_id: int


class ProcessFileRequest(BaseModel):
    user_id: int
    filename: str
    size: int
    mime_type: str


class ProcessFileResponse(BaseModel):
    presigned_url: str
    task_id: uuid.UUID


class TranscribeController(AbstractController):
    """Отвечает за обработку запроса транскрибации аудио в ноты."""

    def __init__(
        self, kafka_client: KafkaClient, redis_client: RedisClient, s3_client: S3Client
    ) -> None:
        super().__init__()
        self._kafka_client = kafka_client
        self._redis_client = redis_client
        self._s3_client = s3_client

    async def handle(self, request: Request) -> Response:
        dispatch = {
            "process-link": self._process_link,
            "process-file": self._process_file,
        }
        handler = dispatch.get(request.state.path)
        if not handler:
            return JSONResponse(404, {"error": "Unknown action"})
        return await handler(request)

    async def _process_link(self, request: ProcessLinkRequest) -> Response:
        task_id = str(uuid.uuid4())
        message_payload = {
            "task_id": task_id,
            "url": str(request.url),
            "user_id": request.user_id,
            "status": TaskStatusesEnum.pending.value,
        }
        self._redis_client.create_task(
            user_id=request.user_id,
            task_id=task_id,
            task_status=TaskStatusesEnum.pending,
        )
        await self._kafka_client.send_message(
            self._kafka_client.process_link_topic,
            message_payload,
        )
        return JSONResponse(202, {"task_id": task_id, "status": "accepted"})

    async def _process_file(self, request: ProcessFileRequest) -> ProcessFileResponse:
        task_id = uuid.uuid4()
        presigned_url = await self._s3_client.get_presigned_url(
            task_id=task_id, key=request.filename
        )
        self._redis_client.create_task(
            file_url=presigned_url,
            user_id=request.user_id,
            task_id=task_id,
            task_status=TaskStatusesEnum.awaiting_upload.value,
        )
        return ProcessFileResponse(presigned_url=presigned_url, task_id=task_id)
