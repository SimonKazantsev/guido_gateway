from contextlib import asynccontextmanager

import httpx
from dependency_injector.wiring import inject
from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import FileResponse
from app.middlewares.middleware import AuthMiddleware
from app.containers import ApplicationContainer


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = ApplicationContainer()
    container.init_resources()
    yield
    container.shutdown_resources()

app = FastAPI(lifespan=lifespan)
app.add_middleware(AuthMiddleware, public_paths = [], token_verifier = None)

async def forward_request(service_url: str, method: str, path: str, body=None, headers=None):
    """Отправка запроса."""
    async with httpx.AsyncClient() as client:
        url = f"{service_url}{path}"
        response = await client.request(method, url, json=body, headers=headers)
        return response


@app.api_route("/{service}/{path:path}", methods=["POST"], response_class=FileResponse)
@inject
async def gateway(
        request: Request,
        file: UploadFile,
        service: str,
    ):
    """Перенаправление запроса в соответствующий микросервис."""

