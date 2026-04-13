from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

import jwt

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

    def _create_token(self, payload: TokenPayload):
        """Создание токена из переданных данных."""
        payload_to_encode = asdict(payload).copy()
        expire = datetime.now(timezone.utc) + timedelta(seconds=self._expires_delta_seconds)
        payload_to_encode.update({"expire": expire})
        return jwt.encode(payload_to_encode, self._key, algorithm=[self._algorithm])

    def verify_token(self, token: str) -> bool:
        jwt.decode(token, self._key, self._algorithm)


        
