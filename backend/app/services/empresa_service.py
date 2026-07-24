from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime

from app.models.shared import ConfiguracionEmpresa
from app.schemas.empresa import UpdateConfiguracionEmpresaRequest
import logging

logger = logging.getLogger(__name__)


async def obtener_configuracion(db: AsyncSession, empresa_id: int) -> ConfiguracionEmpresa:
    """
    Obtiene la configuración de una empresa.
    Si no existe, crea una configuración por defecto.
    """
    query = select(ConfiguracionEmpresa).where(
        ConfiguracionEmpresa.empresa_id == empresa_id
    )
    result = await db.execute(query)
    config = result.scalar_one_or_none()
    
    # Si no existe, crear configuración por defecto
    if not config:
        config = ConfiguracionEmpresa(
            empresa_id=empresa_id,
            serie_factura="F001",
            serie_boleta="B001",
            serie_nc="NC01",
            serie_nd="ND01",
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)
        logger.info(f"Configuración creada para empresa_id={empresa_id}")
    
    return config


async def actualizar_configuracion(
    db: AsyncSession, 
    empresa_id: int,
    data: UpdateConfiguracionEmpresaRequest
) -> ConfiguracionEmpresa:
    """
    Actualiza la configuración de una empresa.
    Solo actualiza los campos que vienen en el request.
    """
    # Obtener config existente (o crear si no existe)
    config = await obtener_configuracion(db, empresa_id)
    
    # Actualizar solo los campos que vienen en el request
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(config, field) and value is not None:
            setattr(config, field, value)
    
    config.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(config)
    
    logger.info(f"Configuración actualizada para empresa_id={empresa_id}")
    
    return config
