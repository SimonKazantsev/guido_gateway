from abc import ABC, abstractmethod

from fastapi import Request, Response


class AbstractAuthProcesser(ABC):
    """Абстрактный обработчик для аутентификации."""

    @abstractmethod
    async def handle(self, request: Request) -> Response:
        ...