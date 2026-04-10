from dataclasses import asdict, dataclass, fields
from datetime import datetime, timedelta, timezone

import jwt


class TokenFieldException(Exception):
    """Исключение, связанное с отсутствием необходимой полезной нагрузки в токене."""

    message = 'Not all required field in Token payload'
    ...

@dataclass
class TokenPayload:
    """Полезная нагрузка, содержащаяся в токене."""
    username: str

class TokenVerifier:
    """Создание и верификация JWT токена."""

    def __init__(self, key: str, algorithm: str, expires_delta_seconds: int):
        self.__key = key
        self.__algorithm = algorithm
        self.__expires_delta_seconds = expires_delta_seconds
    
    def create_token(self, payload: TokenPayload):
        """Создание токена из переданных данных."""
        payload_to_encode = asdict(payload).copy()
        expire = datetime.now(timezone.utc) + timedelta(seconds=self.__expires_delta_seconds)
        payload_to_encode.update({"expire": expire})
        return jwt.encode(payload_to_encode, self.__key, algorithm=[self.__algorithm])

    def get_payload(self, token: str):
        """Получение полезной нагрузки из токена."""
        payload = jwt.decode(token, key=self.__key, algorithms=[self.__algorithm])
        if not self._check_fields(payload):
            raise TokenFieldException(TokenFieldException.message)
    
    def _check_fields(self, data: dict) -> bool:
        """Сверяет поля словаря и датакласса."""
        fields_name = [field.name for field in fields(self.__class__)]
        return all(key in fields_name for key in data)