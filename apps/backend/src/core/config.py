from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # 基础配置
    PROJECT_NAME: str = "Hello Wiki Backend"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = True
    LOG_FILE_PATH: str = "./data/logs/backend.log"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS_COUNT: int = 4

    # 可观测性配置
    OBSERVABILITY_ENABLED: bool = True
    OTEL_ENABLED: bool = True
    OTEL_SERVICE_NAME: str | None = None
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:6006/v1/traces"
    OTEL_EXPORTER_OTLP_HEADERS: str | None = None
    OTEL_INSTRUMENT_FASTAPI: bool = True
    OTEL_INSTRUMENT_LLAMAINDEX: bool = True

    # 数据库与缓存
    DATABASE_URL: str = "postgresql+asyncpg://postgres:vibe_coding@localhost:5432/zhiyuan"
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM 配置 (DeepSeek 默认)
    LLM_API_KEY: str | None = None
    LLM_BASE_URL: str = "https://api.deepseek.com/v1"

    # 存储路径
    STORAGE_BASE_PATH: str = "./data"


settings = Settings()
