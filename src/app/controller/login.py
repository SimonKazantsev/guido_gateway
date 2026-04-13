from abstract import AbstractAuthProcesser


class LoginAuthProcesser(AbstractAuthProcesser):
    """Обработчик сценария 'Вход в систему'."""

    def __init__(self, config: dict) -> None:
        self._service_url = config['auth']   # Пока что реализация такая, далее придумаю что нибудь лучше, сейчас так проще работать.

    async def handle(self, request):
        ...
        