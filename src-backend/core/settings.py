from typing import Optional
from pydantic_settings import BaseSettings
from core.logger_config import logger
from pathlib import Path

_env_path = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    TAVILY_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        env_file = _env_path
        env_file_encoding = "utf-8"


settings = Settings()
