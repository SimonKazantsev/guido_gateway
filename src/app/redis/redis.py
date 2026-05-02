from redis import StrictRedis
from app.enum import TaskStatusesEnum
import json
from app.config import RedisConfig
from pydantic import BaseModel
import uuid
import time


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
        self,
        user_id: str,
        task_id: str,
        file_url: str,
        task_status: TaskStatusesEnum = TaskStatusesEnum.pending.value,
    ) -> None:
        """
        Атомарное создание задачи: сохраняет статус в Redis и добавляет событие в outbox.
        """
        ttl = self._redis_config.ttl_seconds
        task_key = f"task:{task_id}"
        task_data = {
            "user_id": user_id,
            "task_id": task_id,
            "status": task_status,
            "file_url": file_url,
            "created_at": time.time(),
        }

        outbox_event = {
            "task_id": task_id,
            "user_id": user_id,
            "file_url": file_url,
            "event_id": f"evt-{task_id}-{int(time.time() * 1000)}",
        }

        pipe = self._redis.pipeline()
        pipe.setex(task_key, ttl, json.dumps(task_data))
        pipe.rpush("outbox", json.dumps(outbox_event))
        pipe.execute()

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
