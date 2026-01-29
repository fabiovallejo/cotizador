from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_tenant_db, CurrentUser, get_current_user
from app.schemas.clientes import ClienteResponse, ClienteRequest
from app.services.cliente_service import crear_cliente


router = APIRouter(prefix="/api/clientes", tags=["Clientes"])

@router.post(
    "/crear",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear cliente"
)
async def crear(
    data: ClienteRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Registra un nuevo cliente en el sistema.

    ### Parámetros obligatorios:
    - **tipo_documento**: Tipo de identificación (RUC, DNI, PASAPORTE, etc).
    - **numero_documento**: Número de identidad o RUC.
    - **razon_social**: Nombre legal o nombre completo del cliente.

    ### Ejemplo de JSON:
    ```json
    {
        "tipo_documento": "RUC",
        "numero_documento": "20601234567",
        "razon_social": "SERVICIOS TECNOLOGICOS S.A.C.",
        "nombre_comercial": "SERVICIO-TECH",
        "email": "contacto@servitech.pe",
        "telefono": "999888777",
        "direccion_completa": "Av. Las Camelias 456, San Isidro, Lima",
        "ubigeo": "150131",
        "es_cliente_frecuente": false,
        "estado": "activo"
    }
    ```
    """
    cliente = await crear_cliente(db, data)
    return cliente