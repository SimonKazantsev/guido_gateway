
from abstract import AbstractAuthProcesser
from fastapi import Request
from app.app import forward_request
from app.token.token import TokenVerifier
from app.controller.response_handler import ResponseStatusCodeHandler


class RegisterAuthProcesser(AbstractAuthProcesser):
    """Обработчик сценария 'Регистрация'."""

    def __init__(self, config: dict) -> None:
        self._service_url = config['auth']   # Пока что реализация такая, далее придумаю что нибудь лучше, сейчас так проще работать.
    
    async def handle(self, request: Request):
        response = ResponseStatusCodeHandler().handle_response(request)
        token = TokenVerifier.create_token_from_response(response)
        return token