from redis import StrictRedis
from app.enum import TaskStatusesEnum
import json
from app.config import RedisConfig
from pydantic import BaseModel
import uuid
import time


class RedisClient:
    """Клиент для Redis."""

    def __init__(self, redis: StrictRedis, redis_config: RedisConfig) -> None:
        self._redis = redis
        self._redis_config = redis_config

    def create_task(
        self,
        user_id: str,
        task_id: str,
        object_key: str,
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
            "object_key": object_key,
            "created_at": time.time(),
        }

        outbox_event = {
            "task_id": task_id,
            "user_id": user_id,
            "object_key": object_key,
            "event_id": f"evt-{task_id}-{int(time.time() * 1000)}",
        }

        pipe = self._redis.pipeline()
        pipe.setex(task_key, ttl, json.dumps(task_data))
        pipe.rpush("outbox", json.dumps(outbox_event))
        pipe.execute()

    def get_note(self, key: int) :
        return self._redis.get(name=key)

    def cancel_task(self, key: str) -> None:
        """Отмена задачи."""
        task = json.loads(self._redis.get(key))
        task["status"] = TaskStatusesEnum.cancelled.value
        self._redis.set(
            name=key,
            value=task,
        )

    def update_task_status_with_outbox(
            self,
            task_id: str,
            new_status: TaskStatusesEnum,
        ) -> bool:
            task_key = f"task:{task_id}"
            
            task_data_raw = self._redis.get(task_key)
            
            task_data = json.loads(task_data_raw)
            old_status = task_data.get("status")
            
            # Обновляем данные задачи
            task_data["status"] = new_status.value if hasattr(new_status, 'value') else new_status
            task_data["updated_at"] = time.time()
            
            # Создаём событие в outbox
            outbox_event = {
                "task_id": task_id,
                "user_id": task_data.get("user_id"),
                "object_key": task_data.get("object_key"),
                "old_status": old_status,
                "new_status": new_status.value if hasattr(new_status, 'value') else new_status,
                "event_id": f"status-update-{task_id}-{int(time.time() * 1000)}",
                "event_type": "status_changed",
            }
            
            # Атомарно обновляем задачу и добавляем в outbox
            ttl = self._redis.ttl(task_key)
            pipe = self._redis.pipeline()
            
            if ttl > 0:
                pipe.setex(task_key, ttl, json.dumps(task_data))
            else:
                pipe.set(task_key, json.dumps(task_data))
            
            pipe.rpush("outbox", json.dumps(outbox_event))
            pipe.execute()
            
            return True
        
        