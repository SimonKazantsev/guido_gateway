from app.controller.abstract import AbstractController
from fastapi.responses import JSONResponse
from fastapi import Request, Response
from pydantic import ValidationError, BaseModel, HttpUrl
import uuid
from app.kafka.client import KafkaClient


class LinkRequest(BaseModel):
    url: HttpUrl


class TranscribeController(AbstractController):
    """Отвечает за обработку запроса транскрибации аудио в ноты."""

    def __init__(self, kafka_client: KafkaClient) -> None:
        super().__init__()
        self._kafka_client = kafka_client

    async def handle(self, request: Request) -> Response:
        dispatch = {
            "process-link": self._process_link,
            "process-file": self._process_file,
        }
        handler = dispatch.get(request.state.path)
        if not handler:
            return JSONResponse(404, {"error": "Unknown action"})
        return await handler(request)

    async def _process_link(self, request: Request) -> Response:
        try:
            body = await request.json()
            data = LinkRequest(**body)
        except (ValueError, ValidationError) as e:
            return JSONResponse(400, {"error": str(e)})

        task_id = str(uuid.uuid4())
        message_payload = {
            "task_id": task_id,
            "url": str(data.url),
            "user_id": request.state.user_id,
        }
        try:
            await self._kafka_client.send_message(
                self._kafka_client.process_link_topic,
                message_payload,
            )
        except Exception:
            return JSONResponse(500, {"error": "Broker error"})

        return JSONResponse(202, {"task_id": task_id, "status": "accepted"})
