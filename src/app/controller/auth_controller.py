
from fastapi import Request

from app.controller.abstract import AbstractAuthProcesser


class AuthController:
    """Контроллер Аутентификации.
    Отвечает за процедуры аутентификации, регистрицию и вход.
    """

    def __init__(self, processers: dict[AbstractAuthProcesser]) -> None:
        self._processers = processers

    async def process(self, path: str, request: Request):
        """Обработка запроса"""
        return await self._processer['path'].handle(request)