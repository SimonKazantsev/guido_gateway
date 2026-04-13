from http import HTTPStatus
import jwt
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.token.token import TokenException, TokenVerifier


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
            authorization_header = request.headers.get("Authorization")
            token = authorization_header.split(" ")[-1]
            self._token_verifier.verify_token(token)
        except jwt.InvalidTokenError:
            return JSONResponse(status_code=HTTPStatus.UNAUTHORIZED)
