from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
from app.core.dependencies import get_current_user, get_tenant_db, CurrentUser
from app.services.cotizacion_service import (
    crear_cotizacion, 
    listar_cotizaciones, 
    obtener_cotizacion, 
    obtener_items_cotizacion, 
    editar_cotizacion, 
    eliminar_cotizacion,
    convertir_a_factura
)
from app.schemas.cotizacion import (
    CreateCotizacionRequest, 
    CotizacionResponse, 
    ItemCotizacionResponse,
    ConvertirAFacturaResponse
)
from app.models.tenant import Cotizacion, ItemCotizacion, Cliente
from app.models.shared import Empresa, Usuario, CuentaBancaria
from app.services.pdf.pdf_generator import pdf_generator

router = APIRouter(prefix="/api/cotizaciones", tags=["Cotizaciones"])


@router.post(
    "/crear",
    response_model=CotizacionResponse,
    status_code=201,
    summary="Crear cotización",
    description="Crea una nueva cotización con sus items."
)
async def crear_cotizacion_endpoint(
    data: CreateCotizacionRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Crea una nueva cotización.
    
    Ejemplo JSON:
    ```json
    {
        "cliente_id": 1,
        "moneda": "PEN",
        "vigencia_dias": 30,
        "notas_internas": "Cliente frecuente, aplicar descuento",
        "terminos_condiciones": "Precios válidos por 30 días",
        "items": [
            {"producto_id": 1, "cantidad": 5},
            {"producto_id": 2, "cantidad": 3}
        ]
    }
    ```
    """
    cotizacion = await crear_cotizacion(
        db=db,
        data=data,
        usuario_id=current_user.usuario_id
    )
    return cotizacion


@router.get(
    "/listar",
    response_model=list[CotizacionResponse],
    summary="Listar cotizaciones",
    description="Lista cotizaciones con paginación y filtros."
)
async def listar(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(50, ge=1, le=100, description="Máximo de registros"),
    estado: Optional[str] = Query(None, description="Filtrar por estado: borrador | enviada | aceptada | rechazada | convertida"),
    usuario_id: Optional[int] = Query(None, description="Filtrar por vendedor (usuario_id)"),
    busqueda: Optional[str] = Query(None, description="Buscar por número de cotización, razón social o documento del cliente"),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Lista cotizaciones con filtros opcionales.
    
    Estados disponibles:
    - borrador: Editable
    - enviada: No editable
    - aceptada: Puede convertirse a factura
    - rechazada: Final
    - convertida: Ya se convirtió a factura
    """
    cotizaciones = await listar_cotizaciones(
        db=db,
        skip=skip,
        limit=limit,
        estado=estado,
        busqueda=busqueda,
        usuario_id=usuario_id
    )
    return cotizaciones


@router.get(
    "/{id}/pdf",
    summary="Descargar PDF de cotización",
    description="Genera y descarga el PDF de una cotización específica."
)
async def descargar_pdf_cotizacion(
    id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db)
):
    """
    Descarga PDF de cotización.
    
    El PDF incluye:
    - Datos de la empresa
    - Datos del cliente
    - Número de cotización
    - Vigencia/validez en días
    - Items con productos
    - Términos y condiciones
    - Notas internas
    """
    
    # 1. Obtener cotización
    cotizacion = await db.execute(
        select(Cotizacion).where(Cotizacion.id == id)
    )
    cotizacion = cotizacion.scalar_one_or_none()
    
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    # 2. Obtener cliente
    cliente = await db.get(Cliente, cotizacion.cliente_id)
    
    # 3. Obtener items con producto (eager loading)
    items = await db.execute(
        select(ItemCotizacion)
        .options(selectinload(ItemCotizacion.producto))
        .where(ItemCotizacion.cotizacion_id == id)
    )
    items = items.scalars().all()
    
    # 4. Obtener empresa
    empresa = await db.execute(
        select(Empresa).where(Empresa.id == current_user.empresa_id)
    )
    empresa = empresa.scalar_one()
    
    # 5. Obtener vendedor (usuario que creó la cotización)
    vendedor = None
    if cotizacion.usuario_id:
        vendedor_result = await db.execute(
            select(Usuario).where(Usuario.id == cotizacion.usuario_id)
        )
        vendedor = vendedor_result.scalar_one_or_none()
    
    # 6. Obtener cuentas bancarias activas de la empresa
    cuentas_result = await db.execute(
        select(CuentaBancaria).where(
            CuentaBancaria.empresa_id == current_user.empresa_id,
            CuentaBancaria.activo == True,
        )
    )
    cuentas_bancarias = cuentas_result.scalars().all()
    
    # 7. Generar PDF
    pdf_buffer = await pdf_generator.generar_pdf_cotizacion(
        cotizacion=cotizacion,
        cliente=cliente,
        items=items,
        empresa=empresa,
        vendedor=vendedor,
        cuentas_bancarias=cuentas_bancarias,
    )
    
    # 8. Retornar
    return StreamingResponse(
        iter([pdf_buffer.getvalue()]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={cotizacion.numero_cotizacion}.pdf"
        }
    )


@router.get(
    "/{id}",
    response_model=CotizacionResponse,
    summary="Obtener cotización por ID",
    description="Obtiene una cotización específica por su ID."
)
async def obtener(
    id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene una cotización por su ID.
    """
    cotizacion = await obtener_cotizacion(db, id)
    return cotizacion


@router.get(
    "/{id}/items",
    response_model=list[ItemCotizacionResponse],
    summary="Obtener items de una cotización",
    description="Obtiene los items de una cotización específica."
)
async def obtener_items(
    id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene los items de una cotización por su ID.
    """
    items = await obtener_items_cotizacion(db, id)
    return items


@router.put(
    "/{id}",
    response_model=CotizacionResponse,
    summary="Editar cotización",
    description="Edita una cotización. Solo funciona si está en estado 'borrador'."
)
async def editar(
    id: int,
    data: CreateCotizacionRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Edita una cotización. **Solo permite edición si estado = 'borrador'**.
    
    Ejemplo JSON:
    ```json
    {
        "cliente_id": 1,
        "moneda": "PEN",
        "vigencia_dias": 15,
        "items": [
            {"producto_id": 1, "cantidad": 10}
        ]
    }
    ```
    
    Notas:
    - Para agregar items: incluirlos en el array "items"
    - Para eliminar items: no incluirlos en el array "items"
    """
    cotizacion = await editar_cotizacion(db, id, data)
    return cotizacion


@router.delete(
    "/{id}",
    summary="Eliminar cotización",
    description="Elimina una cotización. Solo funciona si está en estado 'borrador'."
)
async def eliminar(
    id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Elimina una cotización (soft delete). **Solo permite si estado = 'borrador'**.
    """
    await eliminar_cotizacion(db, id)
    return {"message": "Cotización eliminada correctamente"}


@router.post(
    "/{id}/convertir-a-factura",
    response_model=ConvertirAFacturaResponse,
    status_code=201,
    summary="Convertir cotización a factura",
    description="Convierte una cotización a factura. Estados permitidos: 'borrador' o 'aceptada'."
)
async def convertir(
    id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Convierte una cotización a factura.
    
    **Estados permitidos**: 'borrador' o 'aceptada'
    
    **Validaciones**:
    - La cotización no debe estar eliminada
    - El cliente no debe estar eliminado
    - Los productos no deben estar eliminados
    - La cotización no debe haber sido convertida antes
    
    **Resultado**:
    - Crea una nueva factura en estado 'borrador' con los datos de la cotización
    - Copia los items con precios CONGELADOS (no se recalculan)
    - Cambia el estado de la cotización a 'convertida'
    """
    result = await convertir_a_factura(
        db=db,
        cotizacion_id=id,
        usuario_id=current_user.usuario_id
    )
    return result
