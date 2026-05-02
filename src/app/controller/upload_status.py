from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import Request
from app.s3.client.client import S3Client
from http import HTTPStatus
from app.redis.redis import RedisClient, RedisTask
from app.enum import TaskStatusesEnum


class UploadStatusRequest(BaseModel):
    task_id: str
    filename: str
    file_size: int
    mime_type: str


class UploadStatusController:
    """Обработчик запроса на проверку статуса задачи."""

    def __init__(self, redis_client: RedisClient, s3_client: S3Client) -> None:
        self._redis_client = redis_client
        self._s3_client = s3_client

    async def handle(
        self, request: Request, upload_status_request: UploadStatusRequest
    ):
        task = self._redis_client.get_task(upload_status_request.task_id)
        if task.user_id != request.state.user_id:
            return JSONResponse(
                status_code=HTTPStatus.FORBIDDEN,
                content={"detail": HTTPStatus.FORBIDDEN.phrase},
            )
        if task.frontend_callback_received:
            return JSONResponse(
                status_code=HTTPStatus.ACCEPTED,
                content={"detail": HTTPStatus.ACCEPTED.phrase},
            )
        task.frontend_callback_received = True
        task.task_status = TaskStatusesEnum.frontend_notified.value
