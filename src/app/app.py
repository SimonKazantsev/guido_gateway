import json
from contextlib import asynccontextmanager

import httpx
from dependency_injector.wiring import Provide, inject
from fastapi import Depends, FastAPI, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.containers import ApplicationContainer
from app.kafka.client import KafkaClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    oauth_scheme = OAuth2PasswordBearer(tokenUrl='token')
    container = ApplicationContainer()
    container.init_resources()
    yield
    container.shutdown_resources()

app = FastAPI(lifespan=lifespan)


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
        #kafka_client: KafkaClient = Depends(Provide[ApplicationContainer.kafka_client]),
    ):
    """Перенаправление запроса в соответствующий микросервис."""
    # if service == 'transcribe':
    #     await kafka_client._s3_client.upload_file(file=file)
    #     await kafka_client._producer.send(
    #         'start_topic',
    #         json.dumps(
    #             {
    #                 "status": "complete",
    #                 "file_key": file.filename,
    #             }
    #         ).encode('utf-8')
    #     )

