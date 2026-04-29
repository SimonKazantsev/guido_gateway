from app.controller.abstract import AbstractController
from fastapi import Request, Response


class TranscribeController(AbstractController):
    """Контроллер транскрибации аудио в ноты."""

    async def handle(self, request: Request) -> Response:
        if request.state.path == "process-link":
            await process_link(request)
        elif request.state.path == "process-file":
            await process_file(request)
