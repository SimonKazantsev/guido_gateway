from app.config import load_config, RedisConfig
from app.redis.redis import RedisClient
from redis import StrictRedis
from functools import partial
from dependency_injector import containers, providers
from dotenv import load_dotenv
from app.token.token import TokenVerifier
from app.s3.client.client import S3Client
from app.htttp_client.client import HTTPClient
from app.controller.auth import AuthController

load_dotenv()


class ApplicationContainer(containers.DeclarativeContainer):
    """Контейнер с различными зависимостями приложения."""

    def prepare_redis(config: RedisConfig):
        return StrictRedis(host=config.host, port=config.port)

    config = load_config()
    wiring_config = containers.WiringConfiguration(packages=["app"])

    http_client = providers.Resource(HTTPClient, config.retry_strategy)

    s3_client = providers.Resource(S3Client, config.storage)

    _redis = partial(prepare_redis, config.redis)

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
    controllers = providers.List(auth_controller)
