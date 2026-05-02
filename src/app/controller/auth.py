from app.controller.abstract import AbstractController
from fastapi import Request, Response
import httpx
from src.app.enum import SERVICE


class AuthController(AbstractController):
    """Контроллер аутентификации."""

    async def handle(self, request: Request) -> Response:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=f"{SERVICE[request.state.service]}/{request.state.path}",
                headers={"Authorization": f"Bearer {request.state.token}"},
            )
            return response.request
