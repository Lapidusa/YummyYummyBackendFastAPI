from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv,find_dotenv
load_dotenv(find_dotenv())
class Settings(BaseSettings):
    SMS_API_KEY: str = os.environ.get('SMS_API_KEY')
    SMS_API_URL: str = os.environ.get('SMS_API_URL')
    DATABASE_URL: str = os.environ.get('DATABASE_URL')
    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY')
    ADMIN_PHONE: str = os.getenv("ADMIN_PHONE")

    class Config:
        env_file = ".env"

settings = Settings()