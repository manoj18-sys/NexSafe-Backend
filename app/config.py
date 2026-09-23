import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "NER-SAFE Backend"
    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./ner_safe.db"
    )

    UPLOAD_DIR: str = os.getenv(
        "UPLOAD_DIR",
        "uploads"
    )

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000"
    ]


settings = Settings()