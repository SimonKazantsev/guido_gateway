from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any
from app.config import StorageConfig
import aiofiles  # type:ignore[import-untyped]
from aiobotocore.session import AioBaseClient, get_session
from botocore.exceptions import ClientError
from fastapi import UploadFile


class S3Client:
    """Клиент для взаимодействия с облачным хранилищем S3."""

    def __init__(self, config: StorageConfig) -> None:
        """Инициализация."""
        self._config = config
        self.session = get_session()

    @asynccontextmanager
    async def _get_client(self) -> AsyncGenerator[Any, AioBaseClient]:
        """Получение клиента сессии."""
        async with self.session.create_client(
            "s3",
            aws_access_key_id=self._config.access_key,
            aws_secret_access_key=self._config.secret_key,
            endpoint_url=self._config.endpoint_url,
        ) as client:
            yield client

    async def upload_file(self, file: UploadFile) -> str:
        """Загрузить объект в хранилище S3. Возвращает ссылку на файл."""
        async with self._get_client() as client:
            await client.put_object(
                Bucket=self._config.bucket_name,
                Key=file.filename,
                Body=file.file,
            )
        return file.filename

    async def get_object(self, key: str) -> None:
        """Получить объект из хранилища S3."""
        async with self._get_client() as client:
            response = await client.get_object(Bucket=self._config.bucket_name, Key=key)
            async with response["Body"] as stream:
                data = await stream.read()
                async with aiofiles.open(key, "wb") as file:
                    await file.write(data)

    async def get_presigned_url(self, task_id: str, key: str) -> str | None:
        """Получить ссылку за прямой загрузки файла в хранилище."""
        object_key = f"uploads/pending/{task_id}/{key}"
        async with self._get_client() as client:
            presigned_url = await client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": self._config.bucket_name,
                    "Key": object_key,
                    "Task_id": task_id,
                },
                ExpiresIn=self._config.presigned_url_expires_seconds,
            )
            return presigned_url

    async def is_healthy(self) -> bool:
        """Проверка работоспособности Файловой БД."""
        try:
            async with self._get_client():
                return True
        except ClientError:
            return False
