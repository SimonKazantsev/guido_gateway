from pydantic import BaseModel


class JWTToken(BaseModel):
    """JWT Токен авторизации."""
    access_token: str
    token_type: str
