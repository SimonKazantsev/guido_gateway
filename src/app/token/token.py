import jwt
from typing import Any
from dataclasses import dataclass


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str


class TokenVerifier:
    """Отвечает за проверку токена."""

    def __init__(
        self,
        public_key: str,
        algorithm: str,
    ):
        self._key = public_key
        self._algorithm = algorithm

    def verify_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, key=self._key, algorithms=self._algorithm)
