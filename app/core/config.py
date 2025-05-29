from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Settings(BaseSettings):
    ENV: str = Field(default="development")
    DATABASE_URL: str | None = None

    SMS_API_KEY: str
    SMS_API_URL: str
    JWT_SECRET_KEY: str
    ADMIN_PHONE: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
