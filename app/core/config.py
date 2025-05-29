from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Settings(BaseSettings):
    ENV: str = Field(default="development")
    DATABASE_URL_LOCAL: str
    DATABASE_URL_HOST: str
    DATABASE_URL: str | None = None

    SMS_API_KEY: str
    SMS_API_URL: str
    JWT_SECRET_KEY: str
    ADMIN_PHONE: str

    @field_validator("DATABASE_URL", mode="before")
    @staticmethod
    def pick_db_url(v, info):
        env = info.data.get("ENV", "development").lower()
        if env == "production":
            return info.data["DATABASE_URL_HOST"]
        return info.data["DATABASE_URL_LOCAL"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
