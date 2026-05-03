from pydantic import BaseModel
import yaml


class RetryConfig(BaseModel):
    retry: int


class StorageConfig(BaseModel):
    access_key: str
    secret_key: str
    bucket_name: str
    endpoint_url: str
    presigned_url_expires_seconds: int


class PublicTokenConfig(BaseModel):
    algorithm: list[str]
    public_token_path: str


class KafkaConfig(BaseModel):
    process_link_topic: str
    outbox_topic: str

class RedisConfig(BaseModel):
    host: str
    port: int
    ttl_seconds: int


class AppConfig(BaseModel):
    retry_strategy: RetryConfig
    storage: StorageConfig
    public_token: PublicTokenConfig
    kafka: KafkaConfig
    redis: RedisConfig


def load_config(config_path: str = "config.yaml"):
    with open(config_path) as config:
        data = yaml.safe_load(config)
        return AppConfig(**data)
