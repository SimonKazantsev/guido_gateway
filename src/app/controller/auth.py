from app.controller.abstract import AbstractController
from fastapi import Request, Response
from src.app.enum import SERVICE


class AuthController(AbstractController):
    """Контроллер аутентификации."""

    async def handle(self, request: Request) -> Response:
        return await self._http_client.send_request(request)
