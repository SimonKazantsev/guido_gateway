import httpx
from app.config import RetryConfig
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from httpx_retries import Retry, RetryTransport
from app.enum import SERVICE

class HTTPClient:
    """Клиент для http запросов."""

    def __init__(self, config: RetryConfig):
        self._retry_strategy = Retry(total=config.retry)

    async def send_request(self, request: Request, json: dict,) -> Response:
        """Отправка запроса."""
        try:
            async with httpx.AsyncClient(
                transport=RetryTransport(retry=self._retry_strategy)
            ) as client:
                response = await client.request(
                    method=request.method,
                    url=f"{SERVICE[request.state.service]}/{request.state.service}/{request.state.path}",
                    json=json,
                )
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service unavailable",
                    "details": f"All retry attempts failed: {str(e)}",
                    "retry_count": 3
                }
            )