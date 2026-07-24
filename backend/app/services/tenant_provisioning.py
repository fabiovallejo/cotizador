from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
from app.core.database import async_engine
from app.models.base import Base
import logging

logger = logging.getLogger(__name__)

async def create_tenant_schema(schema_name: str):
    """
    Crea el schema y TODAS las tablas en el schema especificado.
    """
    try:
        async with async_engine.begin() as conn:
            # 1. Crear schema
            await conn.execute(
                text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
            )
            logger.info(f"Schema {schema_name} creado")
            
            # 2. Setear search_path para que create_all cree en ese schema
            await conn.execute(text(f'SET search_path TO "{schema_name}", public'))
            
            # 3. Crear TODAS las tablas
            await conn.run_sync(Base.metadata.create_all)
            
            logger.info(f"Todas las tablas creadas en {schema_name}")
            
    except Exception as e:
        logger.error(f"Error creando schema {schema_name}: {e}")
        raise