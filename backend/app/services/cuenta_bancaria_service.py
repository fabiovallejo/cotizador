"""
Servicio de Cuentas Bancarias.

CRUD completo con validación de roles inline.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime

from app.models.shared import CuentaBancaria
from app.schemas.cuentas_bancarias import CuentaBancariaCreate, CuentaBancariaUpdate
from app.services.audit_service import registrar_audit
import logging

logger = logging.getLogger(__name__)

# Roles que pueden gestionar cuentas bancarias
ROLES_CREAR = {"admin", "contador", "gerente_ventas"}
ROLES_EDITAR = {"admin", "contador"}
ROLES_ELIMINAR = {"admin"}


async def listar_cuentas_bancarias(
    db: AsyncSession,
    empresa_id: int,
) -> list[CuentaBancaria]:
    """
    Lista todas las cuentas bancarias de la empresa.
    Cualquier usuario autenticado puede ver las cuentas.
    """
    query = (
        select(CuentaBancaria)
        .where(CuentaBancaria.empresa_id == empresa_id)
        .order_by(CuentaBancaria.nombre_banco, CuentaBancaria.moneda)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def crear_cuenta_bancaria(
    db: AsyncSession,
    empresa_id: int,
    data: CuentaBancariaCreate,
    rol: str,
    usuario_id: int = 0,
) -> CuentaBancaria:
    """
    Crea una nueva cuenta bancaria.
    Solo roles: administrador, contador, gerente_ventas.
    """
    if rol not in ROLES_CREAR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear cuentas bancarias"
        )

    cuenta = CuentaBancaria(
        empresa_id=empresa_id,
        nombre_banco=data.nombre_banco,
        numero_cuenta=data.numero_cuenta,
        cci=data.cci,
        moneda=data.moneda,
        tipo_cuenta=data.tipo_cuenta,
        titular=data.titular,
    )
    db.add(cuenta)
    await db.flush()
    
    await registrar_audit(
        db, empresa_id=empresa_id, usuario_id=usuario_id,
        accion="crear_cuenta_bancaria", tabla="cuentas_bancarias",
        registro_id=cuenta.id,
        descripcion=f"{data.nombre_banco} {data.moneda} — {data.numero_cuenta}",
    )
    await db.commit()
    await db.refresh(cuenta)
    
    logger.info(f"Cuenta bancaria creada: {cuenta.nombre_banco} ({cuenta.moneda}) para empresa_id={empresa_id}")
    return cuenta


async def actualizar_cuenta_bancaria(
    db: AsyncSession,
    cuenta_id: int,
    empresa_id: int,
    data: CuentaBancariaUpdate,
    rol: str,
    usuario_id: int = 0,
) -> CuentaBancaria:
    """
    Actualiza una cuenta bancaria.
    Solo roles: administrador, contador.
    """
    if rol not in ROLES_EDITAR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar cuentas bancarias"
        )

    query = select(CuentaBancaria).where(
        CuentaBancaria.id == cuenta_id,
        CuentaBancaria.empresa_id == empresa_id,
    )
    result = await db.execute(query)
    cuenta = result.scalar_one_or_none()

    if not cuenta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuenta bancaria no encontrada"
        )

    update_data = data.model_dump(exclude_unset=True)
    cambios_str = ", ".join(f"{k}: {getattr(cuenta, k, '?')} → {v}" for k, v in update_data.items() if v is not None)
    for field, value in update_data.items():
        if hasattr(cuenta, field) and value is not None:
            setattr(cuenta, field, value)

    cuenta.updated_at = datetime.utcnow()
    
    await registrar_audit(
        db, empresa_id=empresa_id, usuario_id=usuario_id,
        accion="actualizar_cuenta_bancaria", tabla="cuentas_bancarias",
        registro_id=cuenta_id,
        descripcion=f"{cuenta.nombre_banco} — {cambios_str}",
    )
    await db.commit()
    await db.refresh(cuenta)
    
    logger.info(f"Cuenta bancaria {cuenta_id} actualizada para empresa_id={empresa_id}")
    return cuenta


async def eliminar_cuenta_bancaria(
    db: AsyncSession,
    cuenta_id: int,
    empresa_id: int,
    rol: str,
    usuario_id: int = 0,
) -> CuentaBancaria:
    """
    Elimina una cuenta bancaria.
    Solo el administrador puede eliminar.
    """
    if rol not in ROLES_ELIMINAR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador puede eliminar cuentas bancarias"
        )

    query = select(CuentaBancaria).where(
        CuentaBancaria.id == cuenta_id,
        CuentaBancaria.empresa_id == empresa_id,
    )
    result = await db.execute(query)
    cuenta = result.scalar_one_or_none()

    if not cuenta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuenta bancaria no encontrada"
        )

    desc = f"{cuenta.nombre_banco} {cuenta.moneda} — {cuenta.numero_cuenta}"
    await registrar_audit(
        db, empresa_id=empresa_id, usuario_id=usuario_id,
        accion="eliminar_cuenta_bancaria", tabla="cuentas_bancarias",
        registro_id=cuenta_id,
        descripcion=desc,
    )
    await db.delete(cuenta)
    await db.commit()
    
    logger.info(f"Cuenta bancaria {cuenta_id} eliminada para empresa_id={empresa_id}")
    return cuenta
