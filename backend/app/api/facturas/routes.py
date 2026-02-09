from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.dependencies import get_current_user, get_tenant_db, CurrentUser
from app.services.factura_service import crear_factura, listar_facturas, obtener_factura, obtener_items_factura, eliminar_factura, editar_factura
from app.schemas.factura import CreateFacturaRequest, FacturaResponse, ItemFacturaResponse
from app.models.shared import Usuario, Empresa
from app.models.tenant import Factura, ItemFactura, Cliente
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.services.pdf.pdf_generator import pdf_generator
from fastapi.responses import StreamingResponse

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


@router.get("/{id}/pdf")
async def descargar_pdf_factura(
    id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db)
):
    """
    Descarga PDF de factura.
    """
    
    # 1. Obtener factura
    factura = await db.execute(
        select(Factura).where(Factura.id == id)
    )
    factura = factura.scalar_one_or_none()
    
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # 2. Obtener cliente
    cliente = await db.get(Cliente, factura.cliente_id)
    
    # 3. Obtener items con producto (eager loading)
    items = await db.execute(
        select(ItemFactura)
        .options(selectinload(ItemFactura.producto))
        .where(ItemFactura.factura_id == id)
    )
    items = items.scalars().all()
    
    # 4. Obtener empresa
    empresa = await db.execute(
        select(Empresa).where(Empresa.id == current_user.empresa_id)
    )
    empresa = empresa.scalar_one()
    
    # 5. Generar PDF
    
    pdf_buffer = await pdf_generator.generar_pdf_factura(
        factura=factura,
        cliente=cliente,
        items=items,
        empresa=empresa
    )
    
    # 6. Retornar
    return StreamingResponse(
        iter([pdf_buffer.getvalue()]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=F{factura.numero_serie}-{factura.numero_comprobante}.pdf"
        }
    )


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


@router.put(
    "/{id}",
    summary="Editar una factura",
    description="Editar una factura específica por su ID. Solo funciona si la factura está en estado 'borrador'.",
    response_model=FacturaResponse
)
async def editar(
    data: CreateFacturaRequest,
    id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Edita una factura específica por su ID.
    
    **Solo permite edición si la factura está en estado 'borrador'.**
    
    Parámetros:
    - id: ID de la factura (en la URL)
    
    Ejemplo JSON:
    ```json
    {
        "cliente_id": 1,
        "moneda": "PEN",
        "numero_serie": "F001",
        "forma_pago": "Contado",
        "items": [
            {
                "producto_id": 1,
                "cantidad": 5,
                "precio_unitario": 100.00,
                "igv_porcentaje": 18
            },
            {
                "producto_id": 2,
                "cantidad": 3,
                "precio_unitario": 50.00,
                "igv_porcentaje": 18
            }
        ]
    }
    ```
    
    Notas:
    - Para agregar items: incluirlos en el array "items"
    - Para eliminar items: no incluirlos en el array "items"
    """
    
    factura = await editar_factura(db, id, data)
    
    return factura