from dataclasses import asdict, dataclass, fields
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
import jwt
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Any

class TokenFieldException(Exception):
    """Исключение, связанное с отсутствием необходимой полезной нагрузки в токене."""
    ...

class TokenException(Exception):
    """Общее исключение, описывающее проблемы с токеном."""
    ...

@dataclass
class TokenPayload:
    """Полезная нагрузка, содержащаяся в токене."""
    username: str

class TokenVerifier:
    """Создание и верификация JWT токена."""

    def __init__(self, key: str, algorithm: str, expires_delta_seconds: int) -> None:
        self._key = key
        self._algorithm = algorithm
        self._expires_delta_seconds = expires_delta_seconds

    def create_token(self, payload: TokenPayload):
        """Создание токена из переданных данных."""
        payload_to_encode = asdict(payload).copy()
        expire = datetime.now(timezone.utc) + timedelta(seconds=self._expires_delta_seconds)
        payload_to_encode.update({"expire": expire})
        return jwt.encode(payload_to_encode, self._key, algorithm=[self._algorithm])

    def get_payload(self, token: str):
        """Получение полезной нагрузки из токена."""
        payload = jwt.decode(token, key=self._key, algorithms=[self._algorithm])
        if not self._check_fields(payload):
            raise TokenFieldException('Missing required fields')
        return TokenPayload(**payload)
    
    def _check_fields(self, data: dict) -> bool:
        """Сверяет поля словаря и датакласса."""
        fields_name = [field.name for field in fields(self.__class__)]
        return all(key in fields_name for key in data)

    def verify_token_from_request(self, request: Request) -> bool:
        try:
            auth_header = request.headers.get("Authorization")
            token = auth_header.split(' ')[-1] # Формат токена: Bearer *token*
            payload = self._decode_token(token)
            return self._check_fields(payload)  
        except (AttributeError, IndexError, jwt.InvalidTokenError) as token_exception:
            raise TokenException('Invalid token')
    
    def _decode_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, key=self._key, algorithms=[self._algorithm])

        
