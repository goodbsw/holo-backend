from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List
from pathlib import Path

# Get the base directory of your project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    
    # Computed Database URL
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Document Settings
    DOCUMENTS_DIR: str
    ALLOWED_DOCUMENT_TYPES: str  # "docx,pdf" 형식으로 저장
    MAX_DOCUMENT_SIZE: int

    @property
    def ALLOWED_DOCUMENT_TYPES_LIST(self) -> List[str]:
        return self.ALLOWED_DOCUMENT_TYPES.split(',')

    class Config:
        env_file = BASE_DIR / '.env'
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings() -> Settings:
    return Settings() 