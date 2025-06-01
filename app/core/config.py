from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Settings(BaseSettings):
    ENV: str = Field(default="development")
    DATABASE_URL_LOCAL: str | None = None
    DATABASE_URL_HOST: str | None = None
    DATABASE_URL: str | None = None

    SMS_API_KEY: str
    SMS_API_URL: str
    JWT_SECRET_KEY: str
    ADMIN_PHONE: str

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def pick_db_url(cls, v, info):
        if v is not None:
            return v
        env = info.data.get("ENV", "development").lower()
        if env == "production":
            return info.data.get("DATABASE_URL_HOST")
        return info.data.get("DATABASE_URL_LOCAL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
settings = Settings()
