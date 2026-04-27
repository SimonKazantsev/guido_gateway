from contextlib import asynccontextmanager
import httpx
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject
from fastapi import FastAPI, Request

from app.containers import ApplicationContainer

ROUTES: dict[str, str] = {
    "auth": "http://localhost:8001",      # /auth/* -> auth service
}
PUBLIC_PATHS = {
    "auth": ["/auth/login", "/auth/register", "/auth/refresh"],
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    container = ApplicationContainer()
    container.init_resources()
    yield
    container.shutdown_resources()

app = FastAPI(lifespan=lifespan)
@app.api_route("/{service}/{path:path}", methods=['POST'])
async def gateway(
        request: Request,
        service: str,
        path: str,
        json: dict,
    ):
    """Перенаправление запроса в соответствующий микросервис."""
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=f'{ROUTES[service]}/{path}',
            json=json,
        )
        return response.request
