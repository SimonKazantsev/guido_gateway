from pydantic import BaseModel
from app.redis.redis import RedisClient
from app.middleware import TokenMiddleware
from contextlib import asynccontextmanager
from app.controller.abstract import AbstractController
from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI, Request, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.containers import ApplicationContainer
from app.s3.client.client import S3Client

container = ApplicationContainer()
container.init_resources()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    container.shutdown_resources()


app = FastAPI(lifespan=lifespan)
security = HTTPBearer()
app.add_middleware(TokenMiddleware, token_verifier=container.token_verifier())


@inject
@app.api_route("/{service}/{path:path}", methods=["POST"])
async def gateway(
    request: Request,
    service: str,
    path: str,
    controllers: list[AbstractController] = Depends(
        Provide[ApplicationContainer.controllers]
    ),  # noqa: E501
):
    """Перенаправление запроса в соответствующий микросервис."""
    controller = controllers[service]
    return await controller.handle(request)


@app.post("/task/status")
async def check_task_status(task_id: int):
    """Проверка статуса задачи."""
    return task_id  # Пока что выступает в качестве заглушки


@app.delete("/task/cancel")
@inject
async def cancel_task(
    task_id: int,
    redis_client: RedisClient = Depends(Provide[ApplicationContainer.redis_client]),
) -> None:
    """Удаление задачи на обработку."""
    redis_client.cancel_task(task_id)


@app.post("/file/presigned_url")
@inject
async def get_presigned_url(
    key: str, s3_client: S3Client = Depends(Provide[ApplicationContainer.s3_client])
) -> str | None:
    """Проверка статуса задачи."""
    presigned_url = await s3_client.get_presigned_url(key)
    return presigned_url


class UploadStatusRequest(BaseModel):
    task_id: str
    filename: str
    file_size: int
    mime_type: str


@app.post("/task/upload_status")
@inject
async def fetch_upload_status(
    request: Request,
    upload_status_request: UploadStatusRequest,
    redis_client: RedisClient = Depends(Provide[ApplicationContainer.redis_client]),
):
    task = redis_client.get_task(upload_status_request.task_id)
    if task.user_id != request.state.user_id:
        return


@app.post("/file/s3-webhook")
async def process_webhook(
    request: Request, credentials: HTTPAuthorizationCredentials = Security(security)
):
    print(await request.json())
