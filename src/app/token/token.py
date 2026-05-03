from cryptography.hazmat.primitives import serialization
import jwt
from typing import Any
from dataclasses import dataclass
from app.config import PublicTokenConfig


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str


def read_public_key(file_path: str):
    with open(file=file_path, mode="rb") as file:
        public_key = serialization.load_pem_public_key(file.read())
    return public_key


class TokenVerifier:
    """Отвечает за проверку токена."""

    def __init__(self, token_config: PublicTokenConfig):
        self._key = read_public_key(token_config.public_token_path)
        self._algorithm = token_config.algorithm
        self._webhook_token = token_config.webhook_token

    def verify_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, key=self._key, algorithms=self._algorithm)

    @property
    def webhook_token(self):
        return self._webhook_token
