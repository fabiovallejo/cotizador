from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.dependencies import get_current_user, get_tenant_db, CurrentUser
from app.services.factura_service import crear_factura, listar_facturas, obtener_factura, obtener_items_factura, eliminar_factura
from app.schemas.factura import CreateFacturaRequest, FacturaResponse, ItemFacturaResponse

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


@router.get(
    "/listar",
    response_model=list[FacturaResponse],
    summary="Listar facturas",
    description="Lista todas las facturas con paginación y filtros opcionales."
)
async def listar(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(50, ge=1, le=100, description="Máximo de registros"),
    tipo: Optional[str] = Query(None, description="Tipo de comprobante: FACTURA | BOLETA | NOTA_CREDITO | NOTA_DEBITO"),
    estado: Optional[str] = Query(None, description="Filtrar por estado: borrador | pendiente_firma | firmada | pendiente_sunat | aceptada | rechazada"),
    busqueda: Optional[str] = Query(None, description="Buscar por numero de comprobante, razon social del cliente, numero de serie, numero de documento del cliente"),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Lista todas las facturas con paginación y filtros opcionales.
    
    Parámetros:
    - skip: Registros a saltar
    - limit: Máximo de registros
    - tipo: Tipo de comprobante: FACTURA | BOLETA | NOTA_CREDITO | NOTA_DEBITO
    - estado: Filtrar por estado
    - busqueda: Buscar por numero de comprobante, razon social del cliente, numero de serie, numero de documento del cliente
    """
    
    facturas = await listar_facturas(
        db=db,
        skip=skip,
        limit=limit,
        tipo=tipo,
        estado=estado,
        busqueda=busqueda
    )
    
    return facturas


@router.get(
    "/{id}",
    summary="Obtener factura por ID",
    description="Obtiene una factura especifica por su ID",
    response_model=FacturaResponse
)
async def obtener(
    id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene una factura especifica por su ID.
    
    Parámetros:
    - id: ID de la factura
    """
    
    factura = await obtener_factura(db, id)
    
    return factura


@router.get(
    "/{id}/items",
    summary="Obtener items de una factura",
    description="Obtiene los items de una factura específica por su ID",
    response_model=list[ItemFacturaResponse]
)
async def obtener_items(
    id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene los items de una factura especifica por su ID.
    
    Parámetros:
    - id: ID de la factura
    """
    
    items = await obtener_items_factura(db, id)
    
    return items

@router.delete(
    "/{id}",
    summary="Eliminar una factura",
    description="Elimina una factura específica por su ID",
)
async def eliminar(
    id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Elimina una factura específica por su ID.
    
    Parámetros:
    - id: ID de la factura
    """
    
    await eliminar_factura(db, id)
    
    return {"message": "Factura eliminada correctamente"}