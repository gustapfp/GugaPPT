from typing import Optional
from pydantic_settings import BaseSettings
from structlog import get_logger

logger = get_logger()


class Settings(BaseSettings):
    TAVILY_API_KEY: Optional[str] = None
    OPEN_AI_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
