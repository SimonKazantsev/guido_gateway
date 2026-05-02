from redis import StrictRedis
from app.enum import TaskStatusesEnum
import json
from app.config import RedisConfig
from pydantic import BaseModel
import uuid


class RedisTask(BaseModel):
    task_id: uuid.UUID
    user_id: int
    task_status: TaskStatusesEnum
    frontend_callback_received: bool = False
    ttl_seconds: int


class RedisClient:
    """Клиент для Redis."""

    def __init__(self, redis: StrictRedis, redis_config: RedisConfig) -> None:
        self._redis = redis
        self._redis_config = redis_config

    def create_task(
        self, user_id: str, task_id: str, task_status: TaskStatusesEnum
    ) -> None:
        """Создание задачи обработки аудиоданных."""
        redis_task = RedisTask(
            user_id=user_id,
            task_id=task_id,
            task_status=task_status,
            ttl=self._redis_config.ttl_seconds
        )
        self._redis.set(
            name=task_id,
            value=json.dumps(redis_task.model_dump_json()),
            ex=redis_task.ttl_seconds,
        )

    def get_task(self, task_id: str) -> RedisTask:
        return self._redis.get(name=task_id)

    def cancel_task(self, task_id: str) -> None:
        """Отмена задачи."""
        task = json.loads(self._redis.get(task_id))
        task["status"] = TaskStatusesEnum.cancelled.value
        self._redis.set(
            name=task_id,
            value=task,
        )
