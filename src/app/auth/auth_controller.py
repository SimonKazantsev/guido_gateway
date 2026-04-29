from app.auth.schema import AuthRequest
from app.controller.abstract import AbstractController


class AuthController(AbstractController):
    """Контроллер Аутентификации.
    Отвечает за процедуры аутентификации, регистрицию и вход.
    """

    def __init__(self, processers: dict) -> None:
        self._processers = processers

    async def process(self, path: str, auth_request: AuthRequest):
        """Обработка запроса"""
        return await self._processer[path].handle(auth_request)
