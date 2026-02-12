from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_current_user, get_tenant_db, CurrentUser
from app.services.tipo_cambio_service import tipo_cambio_service
from app.models.shared import Usuario

router = APIRouter(prefix="/api/utils", tags=["Utilidades"])


@router.get("/tipo-cambio")
async def obtener_tipo_cambio(
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Obtiene el tipo de cambio del día desde SUNAT.
    Retorna compra y venta.
    """
    tc_data = await tipo_cambio_service.obtener_tc_del_dia()
    return {
        "fecha": tc_data["fecha"],
        "compra": tc_data["compra"],
        "venta": tc_data["venta"],
    }


@router.get("/vendedores")
async def listar_vendedores(
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Lista todos los usuarios de la empresa (para filtros de vendedor).
    Retorna solo id, nombre, apellido y rol.
    Accesible para cualquier usuario autenticado.
    """
    result = await db.execute(
        select(Usuario).where(
            Usuario.empresa_id == current_user.empresa_id,
            Usuario.estado == "activo",
        )
    )
    usuarios = result.scalars().all()
    return [
        {
            "id": u.id,
            "nombre": u.nombre,
            "apellido": u.apellido,
            "rol": u.rol,
        }
        for u in usuarios
    ]
