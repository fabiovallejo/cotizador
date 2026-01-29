from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    environment: str = "development"

    #Base de datos
    db_user: str = "facturacion"
    db_password: str = "SecurePassword123!"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "facturacion_db"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    #Seguridad
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expires_int: int = 60 * 24

    #Redis
    redis_url: str = "redis://localhost:6379/0"

    #Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    #SUNAT
    ambiente_sunat: str = "beta"
    ruta_certificado: Optional[str] = None

    #ADMIN SECRET
    admin_secret_key: str = "dev-admin-secret-key-change-in-production"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()