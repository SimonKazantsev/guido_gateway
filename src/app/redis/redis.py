from redis import StrictRedis
from app.enum import TaskStatusesEnum


class RedisClient:
    """Клиент для Redis."""

    def __init__(self, redis: StrictRedis) -> None:
        self._redis = redis

    def create_task(self, task_id: str, task_status: TaskStatusesEnum) -> None:
        """Создание задачи обработки аудиоданных."""
        self._redis.set(name=task_id, value=task_status)

    def get_task_status(self, task_id: str) -> TaskStatusesEnum:
        return self._redis.get(name=task_id)

    def cancel_task(self, task_id: str):
        """Отмена задачи."""
        self._redis.set(
            name=task_id,
            value=TaskStatusesEnum.cancelled.value,
        )
