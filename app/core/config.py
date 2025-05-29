import os

from pydantic import Field, BaseSettings, field_validator
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Settings(BaseSettings):
    ENV: str = Field(default="development")
    DATABASE_URL_LOCAL: str
    DATABASE_URL_HOST: str
    DATABASE_URL: str | None = None

    SMS_API_KEY: str =  os.environ.get('SMS_API_KEY')
    SMS_API_URL: str = os.environ.get('SMS_API_URL')
    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY')
    ADMIN_PHONE: str = os.getenv("ADMIN_PHONE")

    @field_validator("DATABASE_URL", mode="before")
    def pick_db_url(self, v, info):
        env = info.data.get("ENV", "development").lower()
        if env == "production":
            return info.data["DATABASE_URL_HOST"]
        return info.data["DATABASE_URL_LOCAL"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
