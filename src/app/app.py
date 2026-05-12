from pydantic import BaseModel
import asyncio
import uuid
from app.controller.websocket import listen_for_notifications
from app.redis.redis import RedisClient
from app.middleware import TokenMiddleware
from contextlib import asynccontextmanager
from app.controller.abstract import AbstractController
from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI, Request, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.containers import ApplicationContainer
from app.s3.client.client import S3Client

container = ApplicationContainer()
container.init_resources()


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = ApplicationContainer()
    container.init_resources()
    redis_client = container.redis_client()
    pubsub = redis_client._redis.pubsub()
    manager = container.connection_manager()
    asyncio.create_task(listen_for_notifications(pubsub, manager))
    yield
    container.shutdown_resources()


app = FastAPI(lifespan=lifespan)
security = HTTPBearer(auto_error=False)
app.add_middleware(TokenMiddleware, token_verifier=container.token_verifier())

@app.api_route("/{service:path}", methods=["POST"])
@inject
async def gateway(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    controllers: dict[str, AbstractController] = Depends(Provide[ApplicationContainer.controllers])
):
    """Перенаправление запроса в соответствующий микросервис."""
    controller = controllers[request.state.service]
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
    return await s3_client.get_presigned_url(key)


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
    task = redis_client.get_note(upload_status_request.task_id)
    if task.user_id != request.state.user_id:
        return


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, manager, redis_client):
    connection_id = str(uuid.uuid4())
    
    await manager.connect(connection_id, websocket)
    
    try:
        # Сохраняем связь user_id -> connection_id в Redis
        await redis_client.set(f"user:{user_id}:connection", connection_id)
        
        while True:
            # Ждем сообщения от клиента (если нужно)
            data = await websocket.receive_text()
            
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        await redis_client.delete(f"user:{user_id}:connection")