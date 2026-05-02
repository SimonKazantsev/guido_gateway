from app.redis.redis import RedisClient
from contextlib import asynccontextmanager
import httpx
from app.controller.abstract import AbstractController
from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI, Request, Depends
from app.containers import ApplicationContainer
from src.app.enum import SERVICE


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = ApplicationContainer()
    container.init_resources()
    yield
    container.shutdown_resources()


app = FastAPI(lifespan=lifespan)


@inject
@app.api_route("/{service}/{path:path}", methods=["POST"])
async def gateway(
    request: Request,
    service: str,
    path: str,
    json: dict,
    controllers: list[AbstractController] = Depends(
        Provide[ApplicationContainer.controllers]
    ),  # noqa: E501
):
    """Перенаправление запроса в соответствующий микросервис."""
    controller = controllers[service]
    return await controller.handle(request)


@app.post("/status")
async def check_task_status(task_id: int):
    """Проверка статуса задачи."""
    return task_id  # Пока что выступает в качестве заглушки


@app.delete("/task")
@inject
async def cancel_task(
    task_id: int,
    redis_client: RedisClient = Depends(Provide[ApplicationContainer.redis_client]),
) -> None:
    """Удаление задачи на обработку."""
    redis_client.cancel_task(task_id)
