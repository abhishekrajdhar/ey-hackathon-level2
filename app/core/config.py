from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    project_name: str = "Agentic RFP Backend"
    api_v1_prefix: str = "/api/v1"
    environment: str = "dev"  # dev | staging | prod

    class Config:
        env_file = ".env"
        extra = "ignore"   # ✅ prevents crashes from unknown env vars


@lru_cache
def get_settings() -> Settings:
    return Settings()
