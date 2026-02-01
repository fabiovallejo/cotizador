from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_user, get_tenant_db, CurrentUser
from app.services.empresa_service import obtener_configuracion, actualizar_configuracion
from app.schemas.empresa import ConfiguracionEmpresaResponse, UpdateConfiguracionEmpresaRequest

router = APIRouter(prefix="/api/empresa", tags=["Empresa"])


@router.get(
    "/configuracion",
    response_model=ConfiguracionEmpresaResponse,
    summary="Obtener configuración de empresa",
    description="Obtiene la configuración actual de la empresa."
)
async def get_configuracion(
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene la configuración de la empresa del usuario autenticado.
    
    Incluye:
    - Series de comprobantes (factura, boleta, NC, ND)
    - Ruta del certificado digital
    - Datos para PDF (logo, teléfono, email)
    """
    config = await obtener_configuracion(db, current_user.empresa_id)
    return config


@router.put(
    "/configuracion",
    response_model=ConfiguracionEmpresaResponse,
    summary="Actualizar configuración de empresa",
    description="Actualiza la configuración de la empresa."
)
async def update_configuracion(
    data: UpdateConfiguracionEmpresaRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Actualiza la configuración de la empresa.
    
    Solo se actualizan los campos enviados en el request.
    
    Ejemplo JSON:
    ```json
    {
        "serie_factura": "F002",
        "logo_url": "https://ejemplo.com/logo.png",
        "telefono": "01-234-5678",
        "email": "ventas@empresa.com"
    }
    ```
    """
    config = await actualizar_configuracion(db, current_user.empresa_id, data)
    return config
