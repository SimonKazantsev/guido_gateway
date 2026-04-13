from enum import Enum
from http import HTTPStatus

from httpx import ConnectError, TimeoutException


class AppErrorCode(Enum):
    # Клиентские ошибки
    BAD_REQUEST = ("BAD_REQUEST", HTTPStatus.BAD_REQUEST)
    NOT_FOUND = ("NOT_FOUND", HTTPStatus.NOT_FOUND)
    CONFLICT = ("CONFLICT", HTTPStatus.CONFLICT)
    UNPROCESSABLE = ("UNPROCESSABLE", HTTPStatus.UNPROCESSABLE_ENTITY)
    
    # Серверные ошибки
    INTERNAL_ERROR = ("INTERNAL_ERROR", HTTPStatus.INTERNAL_SERVER_ERROR)
    SERVICE_UNAVAILABLE = ("SERVICE_UNAVAILABLE", HTTPStatus.SERVICE_UNAVAILABLE)
    
    # Сетевые ошибки
    TIMEOUT = ("TIMEOUT", HTTPStatus.GATEWAY_TIMEOUT)
    CONNECTION_ERROR = ("CONNECTION_ERROR", HTTPStatus.BAD_GATEWAY)
    
    def __init__(self, msg: str, http_status: HTTPStatus):
        self.msg = msg
        self.http_status = http_status


HTTP_STATUS_TO_ERROR_CODE = {
    HTTPStatus.BAD_REQUEST: AppErrorCode.BAD_REQUEST,
    HTTPStatus.NOT_FOUND: AppErrorCode.NOT_FOUND,
    HTTPStatus.CONFLICT: AppErrorCode.CONFLICT,
    HTTPStatus.UNPROCESSABLE_ENTITY: AppErrorCode.UNPROCESSABLE,
    HTTPStatus.INTERNAL_SERVER_ERROR: AppErrorCode.INTERNAL_ERROR,
    HTTPStatus.SERVICE_UNAVAILABLE: AppErrorCode.SERVICE_UNAVAILABLE,
}

EXCEPTION_TO_ERROR_CODE = {
    TimeoutException: AppErrorCode.TIMEOUT,
    ConnectError: AppErrorCode.CONNECTION_ERROR,
}