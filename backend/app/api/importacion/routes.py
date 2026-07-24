"""
Endpoints de importación masiva desde Excel.
Solo accesibles por usuarios con rol 'admin'.
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_tenant_db, CurrentUser
from app.services.importacion_service import (
    generar_plantilla_clientes,
    generar_plantilla_productos,
    importar_clientes,
    importar_productos,
)

router = APIRouter(prefix="/api/importacion", tags=["Importación Masiva"])


def _verificar_admin(current_user: CurrentUser):
    """Lanza 403 si el usuario no es admin."""
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden importar datos masivamente.",
        )


# ============================================================================
# PLANTILLAS
# ============================================================================

@router.get(
    "/plantilla/clientes",
    summary="Descargar plantilla Excel de clientes",
    description="Genera y descarga una plantilla Excel con los campos necesarios para importar clientes.",
)
async def descargar_plantilla_clientes(
    current_user: CurrentUser = Depends(get_current_user),
):
    _verificar_admin(current_user)
    buf = generar_plantilla_clientes()
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=plantilla_clientes.xlsx"},
    )


@router.get(
    "/plantilla/productos",
    summary="Descargar plantilla Excel de productos",
    description="Genera y descarga una plantilla Excel con los campos necesarios para importar productos.",
)
async def descargar_plantilla_productos(
    current_user: CurrentUser = Depends(get_current_user),
):
    _verificar_admin(current_user)
    buf = generar_plantilla_productos()
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=plantilla_productos.xlsx"},
    )


# ============================================================================
# IMPORTACIÓN
# ============================================================================

@router.post(
    "/clientes",
    summary="Importar clientes desde Excel",
    description="Sube un archivo Excel con clientes. Inserta por lotes para evitar timeouts.",
)
async def importar_clientes_endpoint(
    file: UploadFile = File(..., description="Archivo .xlsx con datos de clientes"),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    _verificar_admin(current_user)

    if not file.filename or not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .xlsx")

    file_bytes = await file.read()
    if len(file_bytes) > 5 * 1024 * 1024:  # 5MB max
        raise HTTPException(status_code=400, detail="El archivo excede el tamaño máximo de 5MB")

    result = await importar_clientes(db, file_bytes)
    return result


@router.post(
    "/productos",
    summary="Importar productos desde Excel",
    description="Sube un archivo Excel con productos. Inserta por lotes para evitar timeouts.",
)
async def importar_productos_endpoint(
    file: UploadFile = File(..., description="Archivo .xlsx con datos de productos"),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    _verificar_admin(current_user)

    if not file.filename or not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .xlsx")

    file_bytes = await file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="El archivo excede el tamaño máximo de 5MB")

    result = await importar_productos(db, file_bytes)
    return result
