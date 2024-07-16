import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    sqlalchemy_database_url: str
    upload_dir: str = os.path.join(os.path.dirname(__file__), "..", "uploads")

    class Config:
        env_file = ".env"


settings = Settings()
