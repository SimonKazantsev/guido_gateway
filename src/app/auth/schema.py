from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    email: str = Field(
        description='Логин пользователя',
        examples=['skazantsev@mail.ru']
    )
    password: str = Field(
        description='Пароль пользователя',
        examples=['password']
    )
