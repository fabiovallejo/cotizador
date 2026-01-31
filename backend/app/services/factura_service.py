# app/services/factura_service.py

from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import HTTPException, status
from typing import Optional

from app.models.tenant import Factura, ItemFactura, Cliente, Producto
from app.services.tipo_cambio_service import tipo_cambio_service
from app.schemas.factura import CreateFacturaRequest
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)


async def obtener_siguiente_numero_comprobante(
    db: AsyncSession,
    numero_serie: str
) -> str:
    """
    Obtiene el siguiente número de comprobante para una serie.
    Formato: 8 dígitos con ceros a la izquierda (ej: 00000001)
    Usa CAST a INTEGER para comparación numérica correcta.
    """
    from sqlalchemy import Integer
    
    result = await db.execute(
        select(func.max(func.cast(Factura.numero_comprobante, Integer)))
        .where(Factura.numero_serie == numero_serie)
    )
    max_numero = result.scalar_one_or_none()
    
    if max_numero:
        siguiente = max_numero + 1
    else:
        siguiente = 1
    
    return str(siguiente).zfill(8)

async def crear_factura(
    db: AsyncSession,
    data: CreateFacturaRequest,
    empresa_id: int,
    usuario_id: int
):
    
    # 1. Validar cliente (search_path ya está seteado por get_tenant_db)
    cliente = await db.execute(
        select(Cliente).where(Cliente.id == data.cliente_id)
    )
    cliente = cliente.scalar_one_or_none()
    if not cliente:
        raise HTTPException(status_code=400, detail="Cliente no encontrado")

    # 2. Verificar si algún producto necesita conversión
    necesita_tc = False
    for item in data.items:
        producto = await db.execute(
            select(Producto).where(Producto.id == item.producto_id)
        )
        producto = producto.scalar_one_or_none()
        moneda_producto = producto.moneda or "PEN"
        
        if moneda_producto != data.moneda:
            necesita_tc = True
            break
    
    # 3. Obtener TC del día
    tc_del_dia = None
    if necesita_tc:
        try:
            tc_data = await tipo_cambio_service.obtener_tc_del_dia()
            tc_del_dia = Decimal(tc_data["venta"])
            logger.info(f"TC {data.moneda}: {tc_del_dia}")
        except Exception as e:
            logger.error(f"Error obteniendo TC: {e}")
            if not data.tipo_cambio:
                raise HTTPException(
                    status_code=500,
                    detail="No se pudo obtener TC automático de SUNAT"
                )
            tc_del_dia = Decimal(str(data.tipo_cambio))
    
    # 4. Procesar items
    subtotal_factura = Decimal(0)
    igv_total_factura = Decimal(0)
    items_procesados = []
    
    for item in data.items:
        # Obtener producto
        producto = await db.execute(
            select(Producto).where(Producto.id == item.producto_id)
        )
        producto = producto.scalar_one_or_none()
        if not producto:
            raise HTTPException(status_code=400, detail=f"Producto no encontrado")
        
        # ===== CONVERSIÓN DE MONEDA =====
        moneda_producto = producto.moneda or "PEN"
        precio_original = Decimal(str(producto.precio_unitario))
        cantidad = Decimal(str(item.cantidad))
        igv_pct = Decimal(str(item.igv_porcentaje or 18))
        
        # Conversión: Si moneda producto != moneda factura, convertir
        precio_en_factura = precio_original
        tc_usado = None
        
        if moneda_producto != data.moneda:
            # Necesita conversión
            if data.moneda == "PEN":
                # Convertir a PEN (producto está en USD)
                if not tc_del_dia:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No hay TC para convertir {moneda_producto} a {data.moneda}"
                    )
                precio_en_factura = precio_original * tc_del_dia
                tc_usado = tc_del_dia
            
            elif moneda_producto == "PEN" and data.moneda != "PEN":
                # Convertir de PEN a USD/EUR
                if not tc_del_dia:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No hay TC para convertir {moneda_producto} a {data.moneda}"
                    )
                precio_en_factura = precio_original / tc_del_dia
                tc_usado = tc_del_dia
            
            else:

                raise HTTPException(
                    status_code=400,
                    detail=f"Conversión {moneda_producto} a {data.moneda} no soportada"
                )
        
        # ===== CÁLCULOS DEL ITEM =====
        subtotal_item = precio_en_factura * cantidad
        igv_item = subtotal_item * igv_pct / Decimal(100)
        total_item = subtotal_item + igv_item
        
        subtotal_factura += subtotal_item
        igv_total_factura += igv_item
        
        items_procesados.append({
            "producto_id": producto.id,
            "moneda_original": moneda_producto,
            "precio_original": precio_original,
            "tipo_cambio_usado": tc_usado,
            "precio_en_factura": precio_en_factura,
            "cantidad": cantidad,
            "igv_porcentaje": igv_pct,
            "igv_monto": igv_item,
            "subtotal": subtotal_item,
            "total": total_item,
        })
    
    total_factura = subtotal_factura + igv_total_factura

    # 5. Obtener siguiente número de comprobante
    serie = data.numero_serie or "F001"
    numero_comprobante = await obtener_siguiente_numero_comprobante(db, serie)
    
    # 6. Crear factura
    nueva_factura = Factura(
        usuario_id=usuario_id,
        cliente_id=data.cliente_id,
        
        numero_serie=data.numero_serie or "F001",
        numero_comprobante=numero_comprobante, 
        
        moneda=data.moneda,
        tipo_cambio=tc_del_dia,
        
        subtotal=subtotal_factura,
        igv_total=igv_total_factura,
        total=total_factura,
        
        subtotal_en_pen=None, 
        total_en_pen=None,     
        
        tipo_operacion=data.tipo_operacion or "0101",
        forma_pago=data.forma_pago or "Contado",
        
        fecha_emision=datetime.now().date(),
        hora_emision=datetime.now().time(),
        
        estado="borrador",
    )
    
    db.add(nueva_factura)
    await db.flush()
    
    # 7. Crear items
    for item_data in items_procesados:
        nuevo_item = ItemFactura(
            factura_id=nueva_factura.id,
            producto_id=item_data["producto_id"],
            
            moneda_original=item_data["moneda_original"],
            precio_original=item_data["precio_original"],
            tipo_cambio_usado=item_data["tipo_cambio_usado"],
            precio_en_factura=item_data["precio_en_factura"],
            precio_unitario=item_data["precio_en_factura"], 
            
            cantidad=item_data["cantidad"],
            igv_porcentaje=item_data["igv_porcentaje"],
            igv_monto=item_data["igv_monto"],
            subtotal=item_data["subtotal"],
            total=item_data["total"],
            
            tipo_afectacion_igv="10",
        )
        db.add(nuevo_item)
    
    await db.commit()
    await db.refresh(nueva_factura)
    
    return nueva_factura


async def listar_facturas(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    tipo: Optional[str] = None,
    estado: Optional[str] = None, 
    busqueda: Optional[str] = None,
) -> list[Factura]:
    query = select(Factura).where(Factura.deleted_at == None)
    
    if tipo:
        query = query.where(Factura.tipo_comprobante == tipo)
    
    if estado:
        query = query.where(Factura.estado == estado)
    
    if busqueda:
        query = query.where(
            or_(
                Factura.numero_comprobante.ilike(f"%{busqueda}%"),
                Factura.cliente.has(
                    Cliente.razon_social.ilike(f"%{busqueda}%")
                ),
                Factura.cliente.has(
                    Cliente.numero_documento.ilike(f"%{busqueda}%")
                ),
            )
        )
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    facturas = result.scalars().all()
    
    return facturas