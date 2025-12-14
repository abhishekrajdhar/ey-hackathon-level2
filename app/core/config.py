from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    project_name: str = "Agentic RFP Backend"
    api_v1_prefix: str = "/api/v1"
    environment: str = "dev"

    database_url: str = "postgresql+psycopg2://user:password@localhost:5432/rfp_db"
    gemini_api_key: str = "GEMINI_API_KEY"
    gemini_model: str = "models/gemini-2.5-flash"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
