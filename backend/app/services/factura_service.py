# app/services/factura_service.py

from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from fastapi import HTTPException, status

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
    """
    Crea factura con TC automático de SUNAT.
    El search_path ya viene configurado desde get_tenant_db.
    """
    
    # 1. Validar cliente existe
    cliente = await db.execute(
        select(Cliente).where(Cliente.id == data.cliente_id)
    )
    cliente = cliente.scalar_one_or_none()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cliente no encontrado"
        )
    
    # 2. Obtener TC si moneda no es PEN
    tipo_cambio = None
    if data.moneda != "PEN":
        try:
            # Obtener TC de SUNAT automáticamente
            tc_venta = await tipo_cambio_service.obtener_tc_venta_decimal()
            tipo_cambio = tc_venta
            logger.info(f"TC {data.moneda}: {tipo_cambio}")
        except Exception as e:
            logger.error(f"Error obteniendo TC: {e}")
            if not data.tipo_cambio:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No se pudo obtener TC automático de SUNAT"
                )
            tipo_cambio = Decimal(str(data.tipo_cambio))
    
    # 3. Calcular totales
    subtotal = Decimal(0)
    igv_total = Decimal(0)
    
    items_data = []
    for item in data.items:
        # Validar producto
        producto = await db.execute(
            select(Producto).where(Producto.id == item.producto_id)
        )
        producto = producto.scalar_one_or_none()
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Producto {item.producto_id} no encontrado"
            )
        
        # Calcular
        cant = Decimal(str(item.cantidad))
        precio = Decimal(str(item.precio_unitario))
        igv_pct = Decimal(str(item.igv_porcentaje))
        
        item_subtotal = cant * precio
        item_igv = item_subtotal * igv_pct / Decimal(100)
        
        subtotal += item_subtotal
        igv_total += item_igv
        
        items_data.append({
            "producto_id": item.producto_id,
            "cantidad": cant,
            "precio_unitario": precio,
            "igv_porcentaje": igv_pct,
            "igv_monto": item_igv,
            "subtotal": item_subtotal,
            "total": item_subtotal + item_igv,
        })
    
    total = subtotal + igv_total
    
    # 4. Convertir a PEN si es necesario
    subtotal_en_pen = subtotal
    total_en_pen = total
    
    if data.moneda != "PEN" and tipo_cambio:
        subtotal_en_pen = subtotal * tipo_cambio
        total_en_pen = total * tipo_cambio
    
    # 5. Obtener siguiente número de comprobante
    serie = data.numero_serie or "F001"
    numero_comprobante = await obtener_siguiente_numero_comprobante(db, serie)
    
    # 6. Crear factura
    nueva_factura = Factura(
        usuario_id=usuario_id,
        cliente_id=data.cliente_id,
        
        numero_serie=serie,
        numero_comprobante=numero_comprobante,
        
        moneda=data.moneda,
        tipo_cambio=tipo_cambio if data.moneda != "PEN" else None,
        
        subtotal=subtotal,
        igv_total=igv_total,
        total=total,
        
        subtotal_en_pen=subtotal_en_pen,
        total_en_pen=total_en_pen,
        
        tipo_operacion=data.tipo_operacion or "0101",
        forma_pago=data.forma_pago or "Contado",
        
        fecha_emision=datetime.now().date(),
        hora_emision=datetime.now().time(),
        
        estado="borrador",
    )
    
    db.add(nueva_factura)
    await db.flush()
    
    # 6. Crear items
    for item_data in items_data:
        nuevo_item = ItemFactura(
            factura_id=nueva_factura.id,
            producto_id=item_data["producto_id"],
            cantidad=item_data["cantidad"],
            precio_unitario=item_data["precio_unitario"],
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