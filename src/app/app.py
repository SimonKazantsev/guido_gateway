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
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    parts = request.url.path.strip("/").split("/")
    if len(parts) < 2:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"reason": "Invalid path format"},
        )
    service, path = parts[0], "/".join(parts[1:])

    if service not in SERVICE:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"reason": f"Service '{service}' not found"},
        )

    allowed_paths = PATHS.get(service, [])
    if not any(path == allowed or path.startswith(allowed + "/") for allowed in allowed_paths):
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"reason": f"Path '{path}' not allowed for service '{service}'"},
        )

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=HTTPStatus.UNAUTHORIZED,
            content={"reason": "Missing or invalid Authorization header"},
        )
    token = auth_header.split(" ")[1]

    try:
        token_verifier.verify_token(token)
    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=HTTPStatus.UNAUTHORIZED,
            content={"reason": "Invalid or expired token"},
        )

    return await call_next(request)
