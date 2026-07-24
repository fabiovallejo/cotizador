from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_admin_secret
from app.schemas.admin import CreateTenantRequest, CreateTenantResponse
from app.services.tenant_service import onboard_new_tenant
from app.services.tenant_provisioning import create_tenant_schema


router = APIRouter(
    prefix="/api/admin",
    tags=["Administración SaaS"]
)


@router.post(
    "/onboard-company",
    response_model=CreateTenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear empresa y owner",
    description="Endpoint para provisionar nueva empresa (requiere admin secret)",
    responses={
        201: {"description": "Empresa creada exitosamente"},
        400: {"description": "RUC o email duplicado"},
        403: {"description": "Admin secret inválido"},
        500: {"description": "Error interno"},
    }
)
async def create_company_and_owner(
    payload: CreateTenantRequest,
    background_tasks: BackgroundTasks,
    _: str = Depends(verify_admin_secret),
    db: AsyncSession = Depends(get_db)
):
    """
    Crea una nueva empresa y su usuario administrador.
    
    Requiere:
    - Header: x-admin-secret (tu admin_secret_key)
    
    Parámetros:
    - ruc: RUC de 11 dígitos
    - razon_social: Nombre de la empresa
    - direccion: Opcional
    - owner_email: Email del admin
    - owner_nombre: Nombre del admin
    - owner_apellido: Opcional
    - owner_password: Mínimo 8 caracteres, con mayúscula y número
    
    Ejemplo:
    -H "Content-Type: application/json" \
    -H "x-admin-secret: tu-admin-secret" \
    -d '{
        "ruc": "20123456789",
        "razon_social": "ABC Inc",
        "direccion": "Av. Principal 123",
        "owner_email": "admin@abc.com",
        "owner_nombre": "Juan",
        "owner_apellido": "Pérez",
        "owner_password": "SecurePass123"
    }'
    """    
    result = await onboard_new_tenant(db, payload)
    schema_name = f"empresa_{payload.ruc}"
    background_tasks.add_task(create_tenant_schema, schema_name)
    
    return CreateTenantResponse(
        empresa_id=result["empresa_id"],
        owner_id=result["owner_id"],
        owner_email=result["owner_email"],
        owner_nombre=result["owner_nombre"],
        message="Empresa creada. Preparando entorno en background..."
    )