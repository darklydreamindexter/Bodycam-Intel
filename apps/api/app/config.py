from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Bodycam Intelligence Platform"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://bodycam:change-me-locally@postgres:5432/bodycam"
    redis_url: str = "redis://redis:6379/0"
    api_v1_prefix: str = "/api/v1"
    collection_user_agent: str = "BodycamIntel/0.1 (local research collector)"
    collection_max_entries: int = 50

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
