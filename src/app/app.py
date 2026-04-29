from contextlib import asynccontextmanager
import httpx
from app.controller.abstract import AbstractController
from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI, Request, Depends
from app.containers import ApplicationContainer
from app.controller.enum import SERVICE


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
    await controller.handle(request)
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=f"{SERVICE[service]}/{path}",
            json=json,
            headers={"Authorization": f"Bearer {json['token']}"},
        )
        return response.request


@app.post("/status")
async def check_task_status(task_id: int):
    """Проверка статуса задачи."""
    return task_id  # Пока что выступает в качестве заглушки
