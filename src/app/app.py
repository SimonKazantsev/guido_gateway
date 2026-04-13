from contextlib import asynccontextmanager

from dependency_injector.wiring import inject
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.containers import ApplicationContainer
from app.middlewares.middleware import AuthMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = ApplicationContainer()
    container.init_resources()
    yield
    container.shutdown_resources()

app = FastAPI(lifespan=lifespan)
app.add_middleware(AuthMiddleware, public_paths = [], token_verifier = None)

services = ['auth', 'transcribe', 'status']

@app.api_route("/{service}/{path:path}", methods=["POST"])
@inject
async def gateway(
        request: Request,
        service: str,
        path: str,
    ):
    return JSONResponse(status_code=404, content={"detail": "service not found"})
    """Перенаправление запроса в соответствующий микросервис."""

