from functools import lru_cache

from pydantic import BaseSettings


class SkyfiConfig(BaseSettings):
    """
    SkyFi configuration class.
    This class contains all the configuration parameters
    for executing the model inference on SkyFi's infrastructure.
    """

    # Rabbit MQ related
    is_rabbitmq_worker: bool = False
    rabbitmq_host: str = None
    rabbitmq_exchange: str = None
    rabbitmq_req_queue: str = None
    rabbitmq_resp_queue: str = None
    rabbitmq_dl_exchange: str = None
    rabbitmq_dl_queue: str = None

    # FastAPI related
    is_fastapi_server: bool = False
    fastapi_host: str = None
    fastapi_port: int = None

    class Config:
        # Use only SKYFI_ prefixed env vars for settings
        env_prefix = "skyfi_"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings
        ):
            """Ensures that env vars take precedence over config file."""
            return env_settings, init_settings, file_secret_settings


@lru_cache
def load_config() -> SkyfiConfig:
    return SkyfiConfig()
