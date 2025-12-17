
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Entorno
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = ENV == "development"

    # Base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # Seguridad
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_EXPIRATION: int = int(os.getenv("JWT_EXPIRATION", 3600))

    # CORS
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000"
    ).split(",")


settings = Settings()

