from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from http import HTTPStatus
from fastapi.responses import JSONResponse
from app.token.token import TokenVerifier, TokenException

class AuthMiddleware(BaseHTTPMiddleware):
    """Обертка, проверяющая токен пользователя на определённых путях запроса."""

    def __init__(
            self,
            app,
            public_paths: list[str],
            token_verifier: TokenVerifier
        ) -> None:
        super().__init__(app)
        self._public_paths = public_paths
        self._token_verifier = token_verifier

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self._public_paths:
            return await call_next(request)
        try:
            self._token_verifier.verify_token_from_request(request)
        except TokenException:
            return JSONResponse(status_code=HTTPStatus.UNAUTHORIZED)
