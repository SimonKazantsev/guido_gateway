from pydantic import BaseModel
import yaml


class RetryConfig(BaseModel):
    retry: int


class StorageConfig(BaseModel):
    access_key: str
    secret_key: str
    bucket_name: str
    endpoint_url: str


class PublicTokenConfig(BaseModel):
    algorithm: list[str]
    public_token_path: str


class KafkaConfig(BaseModel):
    process_link_topic: str


class AppConfig(BaseModel):
    retry_strategy: RetryConfig
    storage: StorageConfig
    public_token: PublicTokenConfig
    kafka: KafkaConfig


def load_config(config_path: str = "config.yaml"):
    with open(config_path) as config:
        data = yaml.safe_load(config)
        return AppConfig(**data)
