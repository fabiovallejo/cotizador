# app/api/facturas/routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_tenant_db, CurrentUser
from app.services.factura_service import crear_factura
from app.schemas.factura import CreateFacturaRequest, FacturaResponse

router = APIRouter(prefix="/api/facturas", tags=["Facturas"])

@router.post(
    "/crear",
    response_model=FacturaResponse,
    status_code=201,
    summary="Crear factura",
    description="Crea una factura. TC se obtiene automáticamente de SUNAT si es USD."
)
async def crear_factura_endpoint(
    data: CreateFacturaRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Crea una nueva factura.
    
    Si moneda es USD:
    - Obtiene TC automáticamente de SUNAT
    - User puede especificar TC diferente (opcional)
    
    Si moneda es PEN:
    - Usa precio directo, sin conversión
    
    Parámetros:
    - cliente_id: ID del cliente
    - moneda: PEN (default) o USD
    - tipo_cambio: (opcional) TC específico si moneda=USD
    - numero_serie: (opcional) F001, B001, etc
    - items: Lista de items con producto_id, cantidad, precio
    """
    
    factura = await crear_factura(
        db=db,
        data=data,
        empresa_id=current_user.empresa_id,
        usuario_id=current_user.usuario_id
    )
    
    return factura
