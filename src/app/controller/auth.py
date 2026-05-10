from pydantic import BaseModel, ValidationError, EmailStr, field_validator
import re
from app.controller.abstract import AbstractController
from fastapi import Request, Response
import httpx
from src.app.enum import SERVICE

class LoginRequest(BaseModel):
    """Запрос на вход в систему."""
    fingerprint: str
    identifier: str
    password: str

pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'  # noqa:E501


def validate_password(password: str) -> str:
    """
    Правила валидации пароля.
        Длина пароля минимум 8 символов,
        в пароле должны присутствовать малые и заглавные буквы,
        1 спецсимвол: @!%*#?&,
        1 цифра
    """
    if re.match(pattern, password):
        return password
    raise ValueError('password does not meet security requirements')


class UserData(BaseModel):
    """Пользовательские данные для клиентской БД."""
    username: str
    email: EmailStr | None
    password: str

    @field_validator('password')
    def valid_password(cls, value):
        return validate_password(value)

class AuthController(AbstractController):
    """Контроллер аутентификации."""

    async def handle(self, request: Request, json: dict) -> Response:
        if request.state.path == 'register':
            return await self._handle_register(request, json)
        return await self._handle_login(request, json)

    async def _handle_register(self, request: Request, json: dict):
        async with httpx.AsyncClient() as client:
            try:
                UserData(**json)
            except ValidationError:
                return ValidationError
            response = await client.request(
                method=request.method,
                url=f"{SERVICE[request.state.service]}/{request.state.service}/{request.state.path}",
                json=json,
            )   
            return Response(
                content=response.content,
                status_code=response.status_code,
            )
    
    async def _handle_login(self, request: Request, json: dict):
        async with httpx.AsyncClient() as client:
            try:
                LoginRequest(**json)
            except Exception:
                return ValidationError
            response = await client.request(
                method=request.method,
                url=f"{SERVICE[request.state.service]}/{request.state.service}/{request.state.path}",
                json=json,
            )   
            return Response(
                content=response.content,
                status_code=response.status_code,
            )