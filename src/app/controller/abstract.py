from abc import ABC, abstractmethod

from fastapi import Request, Response

from app.htttp_client.client import HTTPClient


class AbstractController(ABC):
    """Абстрактный контроллер для обработки запроса"""

    def __init__(self, http_client: HTTPClient) -> None:
        self._http_client = http_client
    
    @abstractmethod
    async def handle(self, request: Request) -> Response:
        ...

class AuthController(AbstractController):
    """Контроллер аутентификации."""

    async def handle(self, request: Request) -> Response:
        ...

class RegisterController(AuthController):
    """Контроллер регистрации."""

    async def handle(self, request: Request) -> Response:
        ...

class LoginController(AuthController):
    """Контроллер входа в систему."""

    async def handle(self, request: Request) -> Response:
        ...
