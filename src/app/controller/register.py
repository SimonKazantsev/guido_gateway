from http import HTTPStatus

from abstract import AbstractAuthProcesser
from fastapi import HTTPException, Request, Response

from app.htttp_client.client import HTTPClient
from app.token.token import TokenVerifier


class RegisterAuthProcesser(AbstractAuthProcesser):
    """Обработчик сценария 'Регистрация'."""

    def __init__(self, config: dict) -> None:
        self._service_url = config['auth']   # Пока что реализация такая, далее придумаю что нибудь лучше, сейчас так проще работать.
    
    async def handle(
        self,
        request: Request,
        http_client: HTTPClient,
        token_verifier: TokenVerifier):
        response = await http_client.send_request(request)
        token = token_verifier.create_token_from_response(response)
        return token

    async def handle_response_status_code(response: Response) -> Response:
        """Обработать ответ сервера на статус кода."""
        if response.status_code != HTTPStatus.CREATED:
            raise HTTPException(status_code=response.status_code, detail=response.body.get("error"))
        return response
    