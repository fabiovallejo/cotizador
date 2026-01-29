from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.dependencies import get_tenant_db, CurrentUser, get_current_user
from app.schemas.clientes import ClienteResponse, ClienteRequest
from app.services.cliente_service import crear_cliente, listar_clientes, actualizar_cliente


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


@router.get(
    "/listar",
    response_model=list[ClienteResponse],
    summary="Listar clientes"
)
async def listar(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(50, ge=1, le=100, description="Máximo de registros"),
    estado: Optional[str] = Query(None, description="Filtrar por estado: activo | inactivo"),
    busqueda: Optional[str] = Query(None, description="Buscar por razón social, RUC o nombre comercial"),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Lista todos los clientes con paginación y filtros opcionales."""
    clientes = await listar_clientes(db, skip, limit, estado, busqueda)
    return clientes


@router.put(
    "/actualizar/{id}",
    response_model=ClienteResponse,
    summary="Actualizar cliente"
)
async def actualizar(
    id: int,
    data: ClienteRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Actualiza cliente existente"""
    cliente = await actualizar_cliente(db, id, data)
    return cliente