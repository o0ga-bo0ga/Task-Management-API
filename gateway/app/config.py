from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    AUTH_SERVICE_URL: str
    TASK_SERVICE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf8",
        extra="ignore")

@lru_cache
def get_settings():
    return Settings()