from fastapi import Request, Response, HTTPException
from http import HTTPStatus
from httpx import TimeoutException, ConnectError
from app.htttp_client.client import HTTPClient
from app.controller.enum import AppErrorCode


HTTP_STATUS_TO_ERROR_CODE = {
    HTTPStatus.BAD_REQUEST: AppErrorCode.BAD_REQUEST,
    HTTPStatus.NOT_FOUND: AppErrorCode.NOT_FOUND,
    HTTPStatus.CONFLICT: AppErrorCode.CONFLICT,
    HTTPStatus.UNPROCESSABLE_ENTITY: AppErrorCode.UNPROCESSABLE,
    HTTPStatus.INTERNAL_SERVER_ERROR: AppErrorCode.INTERNAL_ERROR,
    HTTPStatus.SERVICE_UNAVAILABLE: AppErrorCode.SERVICE_UNAVAILABLE,
}


class ResponseStatusCodeHandler:
    """Обработчик ответа сервиса на предмет статус кода. 
    """
    def __init__(self, http_client: HTTPClient):
        self._http_client = http_client
    
    async def handle_response(self, request: Request) -> Response:
        """Обработать ответ сервера на статус кода."""
        try:
            response = await self._http_client.send_request(request)
        except (TimeoutException, ConnectError):
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail=HTTPStatus.SERVICE_UNAVAILABLE.description
            )
        except Exception:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=HTTPStatus.INTERNAL_SERVER_ERROR.description,
            )
        if response.status_code != HTTPStatus.CREATED:
            raise HTTPException(status_code=response.status_code, detail=response.body.get("error"))
        return response
        
        



