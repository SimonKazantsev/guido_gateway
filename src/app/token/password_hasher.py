from pwdlib import PasswordHash


class PasswordHasher:
    """Занимается хэшированием паролей."""

    def __init__(self,) -> None:
        self._password_hash:PasswordHash = PasswordHash.recommended()

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Верификация пароля."""
        return self._password_hash.verify(password, hashed_password)
    
    def password_hash(self, password: str) -> str:
        """Хэширование пароля. Возвращает хэш."""
        return self._password_hash.hash(password)
