# app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    USER: str
    PASSWORD: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TESSERACT_CMD: str = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()