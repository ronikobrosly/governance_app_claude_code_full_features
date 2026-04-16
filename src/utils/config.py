"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """CloudGov platform configuration."""

    model_config = {"env_prefix": "CLOUDGOV_"}

    # Database
    database_url: str = "postgresql+asyncpg://localhost:5432/cloudgov"
    test_database_url: str = "postgresql+asyncpg://localhost:5432/cloudgov_test"
    db_pool_size: int = 20
    db_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]

    # ETL
    etl_batch_size: int = 500
    etl_max_retries: int = 3
    etl_retry_backoff_base: float = 2.0

    # Observability
    log_level: str = "INFO"
    enable_tracing: bool = True
    service_name: str = "cloudgov-platform"


settings = Settings()
