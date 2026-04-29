import jwt
from app.token.token import TokenVerifier
from contextlib import asynccontextmanager
import httpx
from typing import Callable
from app.controller.abstract import AbstractController
from http import HTTPStatus
from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from app.containers import ApplicationContainer

SERVICE: dict[str, str] = {
    "auth": "http://localhost:8001",  # /auth/* -> auth service
    "transcribe": "http://localhost:8002",
}
PATHS = {
    "transcribe": ["process-link", "process-file"],
    "auth": [
        "login",
        "logout",
        "register",
        "refresh",
        "delete",
        "change-password",
        "check-username",
    ],
}
PUBLIC_PATHS = [
    "/",
    "/auth/login",
    "/auth/register",
    "/auth/refresh",
    "/docs",
    "/openapi.json",
]


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


@app.middleware("http")
@inject
async def handle_access(
    request: Request,
    call_next: Callable,
    token_verifier: TokenVerifier = Depends(Provide[ApplicationContainer.token_verifier]),
):
    service = request.url.path.split('/')[1]
    path = request.url.path.split('/')[2]
    if service not in SERVICE.keys():
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"reason": HTTPStatus.NOT_FOUND.phrase},
    )
    if path not in PATHS[service]:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"reason": HTTPStatus.NOT_FOUND.phrase},
    )
    try:
        #token = request.headers.get("Authorization").split(' ')[:-1]  # Authorization: Bearer token_here
        token_verifier.verify_token('token')
        return await call_next(request)
    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=HTTPStatus.UNAUTHORIZED,
            content={"reason": HTTPStatus.UNAUTHORIZED.phrase},
        )
