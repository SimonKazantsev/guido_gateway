import jwt
from app.token.token import TokenVerifier
from typing import Callable
from http import HTTPStatus
from dependency_injector.wiring import inject, Provide
from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from app.containers import ApplicationContainer
from src.app.enum import PUBLIC_PATHS, SERVICE, PATHS


@inject
async def handle_access(
    request: Request,
    call_next: Callable,
    token_verifier: TokenVerifier = Depends(
        Provide[ApplicationContainer.token_verifier]
    ),
):
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
        path == allowed or path.startswith(allowed + "/") for allowed in allowed_paths
    ):
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"reason": f"Path '{path}' not allowed for service '{service}'"},
        )

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=HTTPStatus.UNAUTHORIZED,
            content={"reason": "Missing or invalid Authorization header"},
        )
    token = auth_header.split(" ")[1]

    try:
        token_payload = token_verifier.verify_token(token)
        request.state.user_id = token_payload["user_id"]
    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=HTTPStatus.UNAUTHORIZED,
            content={"reason": "Invalid or expired token"},
        )

    return await call_next(request)
