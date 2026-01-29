from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool

from app.models.shared import Empresa, Usuario
from app.core.security import hash_password
from app.schemas.admin import CreateTenantRequest
import logging

logger = logging.getLogger(__name__)


async def onboard_new_tenant(
    db: AsyncSession,
    data: CreateTenantRequest
) -> Dict[str, Any]:
    """
    Crea una empresa y su usuario admin en una transacción atómica.
    """
    
    # Verificar si el RUC ya existe
    ruc_result = await db.execute(
        select(Empresa).where(Empresa.ruc == data.ruc)
    )
    if ruc_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El RUC ya está registrado"
        )

    # Verificar si el email ya existe
    email_result = await db.execute(
        select(Usuario).where(Usuario.email == data.owner_email)
    )
    if email_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email del usuario ya está registrado"
        )

    try:
        # ===== CREAR EMPRESA =====
        schema_name = f"empresa_{data.ruc}"
        
        nueva_empresa = Empresa(
            ruc=data.ruc,
            razon_social=data.razon_social,
            direccion=data.direccion,
            db_schema=schema_name,
            estado="activa"
        )
        db.add(nueva_empresa)
        
        # Flush: asigna ID pero no confirma transacción
        await db.flush()

        # ===== CREAR OWNER =====
        hashed_password = await run_in_threadpool(
            hash_password,
            data.owner_password
        )

        nuevo_owner = Usuario(
            empresa_id=nueva_empresa.id, 
            email=data.owner_email,
            password_hash=hashed_password,
            nombre=data.owner_nombre,
            apellido=data.owner_apellido,
            rol="admin",
            estado="activo"
        )
        db.add(nuevo_owner)

        # ===== CONFIRMAR TRANSACCIÓN =====
        await db.commit()
        
        # Refrescar para obtener IDs generados
        await db.refresh(nueva_empresa)
        await db.refresh(nuevo_owner)

        return {
            "empresa_id": nueva_empresa.id,
            "owner_id": nuevo_owner.id,
            "owner_email": nuevo_owner.email,
            "owner_nombre": nuevo_owner.nombre
        }

    except Exception as e:
        await db.rollback()
        import traceback
        logger.error(f"Error en onboard_new_tenant: {str(e)}")
        logger.error(traceback.format_exc())  # ← Muestra stack trace completo
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear empresa: {str(e)}"  # ← Muestra el error real
        )