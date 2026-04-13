import httpx
from fastapi import Request, Response
from httpx_retries import Retry, RetryTransport


class HTTPClient:
    """Клиент для http запросов."""

    def __init__(self, config: dict):
        self._retry_strategy = Retry(total = config['retry'])
    async def send_request(self, request: Request) -> Response:
        """Отправка запроса."""
        async with httpx.AsyncClient(transport=RetryTransport(retry=self._retry_strategy)) as client:
            response = await client.request(
                method=request.method,
                url=request.url,
                json=await request.body(),
                headers=request.headers,
                timeout=2
            )
            return response