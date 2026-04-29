import os

from dependency_injector import containers, providers
from dotenv import load_dotenv
from app.token.token import TokenVerifier
from app.key import read_public_key
from app.s3.client.client import S3Client

load_dotenv()


class ApplicationContainer(containers.DeclarativeContainer):
    """Контейнер с различными зависимостями приложения."""

    wiring_config = containers.WiringConfiguration(
        packages=["app"]
    )

    s3_client = providers.Resource(
        S3Client,
        access_key=os.getenv("ACCESS_KEY"),
        secret_key=os.getenv("SECRET_KEY"),
        endpoint_url=os.getenv("ENDPOINT_URL"),
        bucket_name=os.getenv("BUCKET_NAME"),
    )

    token_verifier = providers.Resource(
        TokenVerifier,
        public_key=read_public_key(),
        algorithm=["RS256"],
    )

    controllers = 1
