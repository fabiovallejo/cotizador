from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    environment: str = "development"

    # Base de datos
    db_user: str = "facturacion"
    db_password: str = "SecurePassword123!"
    db_host: str = "postgres"
    db_port: int = 5432
    db_name: str = "facturacion_db"

    @property
    def database_url(self) -> str:
        # PRIORIDAD 1: Si existe DATABASE_URL en env, usarla
        env_database_url = os.getenv("DATABASE_URL")
        if env_database_url:
            return env_database_url
        
        # PRIORIDAD 2: Construir desde componentes
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # Seguridad
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expires_int: int = 60 * 24

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # SUNAT
    ambiente_sunat: str = "beta"
    ruta_certificado: Optional[str] = None
    # Token público del endpoint de consulta de tipo de cambio de SUNAT.
    # Puede sobreescribirse con SUNAT_TOKEN sin cambiar el código.
    sunat_token: str = "koai6z623bdhh902ymj3c8lrxzwxivtk22e484my51d7eud23g7z"

    # ADMIN SECRET
    admin_secret_key: str = "dev-admin-secret-key-change-in-production"

    # OpenAI (SDK Agents)
    openai_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
