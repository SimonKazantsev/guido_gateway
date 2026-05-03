import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from app.token.token import TokenVerifier
from http import HTTPStatus
from fastapi.responses import JSONResponse
from src.app.enum import PUBLIC_PATHS, SERVICE, PATHS


class TokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, token_verifier: TokenVerifier):
        super().__init__(app)
        self._token_verifier = token_verifier

    async def dispatch(self, request, call_next):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        parts = request.url.path.strip("/").split("/")
        if len(parts) < 2:
            return JSONResponse(
                status_code=HTTPStatus.NOT_FOUND,
                content={"reason": "Invalid path format"},
            )
        service, path = parts[0], "/".join(parts[1:])
        request.state.service = service
        request.state.path = path

        if service not in SERVICE:
            return JSONResponse(
                status_code=HTTPStatus.NOT_FOUND,
                content={"reason": f"Service '{service}' not found"},
            )

        allowed_paths = PATHS.get(service, [])
        if not any(
            path == allowed or path.startswith(allowed + "/")
            for allowed in allowed_paths
        ):
            return JSONResponse(
                status_code=HTTPStatus.NOT_FOUND,
                content={
                    "reason": f"Path '{path}' not allowed for service '{service}'"
                },
            )

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content={"reason": "Missing or invalid Authorization header"},
            )
        token = auth_header.split(" ")[1]
        try:
            if request.url.path == "/file/s3-webhook":
                if token != self._token_verifier.webhook_token:
                    raise jwt.InvalidTokenError
                return await call_next(request)
            token_payload = self._token_verifier.verify_token(token)
            if token_payload:
                request.state.user_id = token_payload["user_id"]
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content={"reason": "Invalid or expired token"},
            )

        return await call_next(request)
