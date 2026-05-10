from app.config import load_config, RedisConfig
from app.redis.redis import RedisClient
from redis import StrictRedis
from app.kafka.client import KafkaClient
from functools import partial
from dependency_injector import containers, providers
from dotenv import load_dotenv
from app.token.token import TokenVerifier
from app.s3.client.client import S3Client
from app.htttp_client.client import HTTPClient
from app.controller.auth import AuthController
from app.controller.transcribe import TranscribeController
from app.controller.webhook import WebhookController 

load_dotenv()


class ApplicationContainer(containers.DeclarativeContainer):
    """Контейнер с различными зависимостями приложения."""

    def prepare_redis(config: RedisConfig): 
        _redis = StrictRedis(host=config.host, port=config.port)
        return _redis

    config = load_config()

    wiring_config = containers.WiringConfiguration(packages=["app"])

    kafka_client = providers.Resource(KafkaClient, config.kafka)

    http_client = providers.Resource(HTTPClient, config.retry_strategy)

    s3_client = providers.Resource(S3Client, config.storage)

    _redis = providers.Resource(StrictRedis, config.redis.host, config.redis.port)

    redis_client = providers.Resource(
        RedisClient,
        _redis,
        config.redis,
    )

    token_verifier = providers.Resource(
        TokenVerifier,
        config.public_token,
    )

    auth_controller = providers.Resource(
        AuthController,
        http_client,
    )

    transcribe_controller = providers.Resource(
        TranscribeController,
        kafka_client,
        redis_client,
        s3_client,
    )

    webhook_controller = providers.Resource(
        WebhookController,
        http_client
    )
    
    controllers = providers.Dict(
        {
            "auth": auth_controller,
            "transcribe": transcribe_controller,
            "s3-webhook": webhook_controller,
        }
    )