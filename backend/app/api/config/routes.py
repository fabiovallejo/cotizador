"""
Rutas de Configuración:
- CRUD de Cuentas Bancarias
- Audit Logs (paginación con total_count)
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.core.dependencies import get_current_user, get_tenant_db, CurrentUser
from app.services.cuenta_bancaria_service import (
    listar_cuentas_bancarias,
    crear_cuenta_bancaria,
    actualizar_cuenta_bancaria,
    eliminar_cuenta_bancaria,
)
from app.schemas.cuentas_bancarias import (
    CuentaBancariaCreate,
    CuentaBancariaUpdate,
    CuentaBancariaResponse,
)
from app.models.shared import AuditGlobal, Usuario

router = APIRouter(prefix="/api/config", tags=["Configuración"])


# ============================================================================
# CUENTAS BANCARIAS
# ============================================================================

@router.get(
    "/cuentas-bancarias",
    response_model=list[CuentaBancariaResponse],
    summary="Listar cuentas bancarias",
)
async def get_cuentas_bancarias(
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await listar_cuentas_bancarias(db, current_user.empresa_id)


@router.post(
    "/cuentas-bancarias",
    response_model=CuentaBancariaResponse,
    summary="Crear cuenta bancaria",
)
async def post_cuenta_bancaria(
    data: CuentaBancariaCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await crear_cuenta_bancaria(
        db, current_user.empresa_id, data, current_user.rol,
        usuario_id=current_user.usuario_id,
    )


@router.put(
    "/cuentas-bancarias/{id}",
    response_model=CuentaBancariaResponse,
    summary="Actualizar cuenta bancaria",
)
async def put_cuenta_bancaria(
    id: int,
    data: CuentaBancariaUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await actualizar_cuenta_bancaria(
        db, id, current_user.empresa_id, data, current_user.rol,
        usuario_id=current_user.usuario_id,
    )


@router.delete(
    "/cuentas-bancarias/{id}",
    response_model=CuentaBancariaResponse,
    summary="Eliminar cuenta bancaria",
)
async def delete_cuenta_bancaria(
    id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await eliminar_cuenta_bancaria(
        db, id, current_user.empresa_id, current_user.rol,
        usuario_id=current_user.usuario_id,
    )


# ============================================================================
# AUDIT LOGS — paginado con total_count
# ============================================================================

@router.get(
    "/audit-logs",
    summary="Listar logs de auditoría (paginado)",
)
async def get_audit_logs(
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    if current_user.rol not in {"administrador", "contador"}:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver los logs de auditoría"
        )

    base_filter = AuditGlobal.empresa_id == current_user.empresa_id

    # Total count
    count_q = select(func.count(AuditGlobal.id)).where(base_filter)
    total = (await db.execute(count_q)).scalar() or 0

    # Paginated results
    offset = (page - 1) * limit
    query = (
        select(AuditGlobal)
        .where(base_filter)
        .order_by(desc(AuditGlobal.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    logs = result.scalars().all()

    # Resolve user names in a single query
    user_ids = list({log.usuario_id for log in logs})
    user_map: dict[int, str] = {}
    if user_ids:
        users_q = select(Usuario.id, Usuario.nombre, Usuario.apellido).where(Usuario.id.in_(user_ids))
        users_result = await db.execute(users_q)
        for uid, nombre, apellido in users_result:
            user_map[uid] = f"{nombre} {apellido or ''}".strip()

    return {
        "items": [
            {
                "id": log.id,
                "usuario_id": log.usuario_id,
                "usuario_nombre": user_map.get(log.usuario_id, "Desconocido"),
                "accion": log.accion,
                "tabla": log.tabla,
                "registro_id": log.registro_id,
                "descripcion": log.descripcion,
                "ip_usuario": log.ip_usuario,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": max(1, (total + limit - 1) // limit),
    }
