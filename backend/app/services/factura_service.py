# app/services/factura_service.py

from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import HTTPException, status
from typing import Optional

from app.models.tenant import Factura, ItemFactura, Cliente, Producto, Secuencia
from app.services.tipo_cambio_service import tipo_cambio_service
from app.schemas.factura import CreateFacturaRequest
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)


async def obtener_siguiente_numero_comprobante(
    db: AsyncSession,
    numero_serie: str,
    tipo_documento: str = "01"
) -> str:
    """
    Obtiene el siguiente número de comprobante usando la tabla secuencias.
    
    Usa FOR UPDATE para lockear la fila y evitar race conditions
    cuando múltiples usuarios crean facturas simultáneamente.
    
    SUNAT exige numeración CONSECUTIVA sin saltos.
    
    Args:
        db: Sesión de base de datos
        numero_serie: Serie del comprobante (F001, B001, etc)
        tipo_documento: Tipo SUNAT (01=Factura, 03=Boleta, 07=NC, 08=ND)
    
    Returns:
        Número de comprobante formateado con 8 dígitos (ej: 00000001)
    """
    
    # 1. Obtener secuencia y lockear para actualización
    resultado = await db.execute(
        select(Secuencia)
        .where(
            Secuencia.serie == numero_serie,
            Secuencia.tipo_documento == tipo_documento
        )
        .with_for_update()  # LOCK: Evita race condition
    )
    secuencia = resultado.scalar_one_or_none()
    
    if not secuencia:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Serie {numero_serie} no configurada para tipo de documento {tipo_documento}. "
                   f"Contacte al administrador para configurar la secuencia."
        )
    
    # 2. Obtener número actual
    numero_actual = secuencia.proximo_numero
    
    # 3. Incrementar para próxima vez
    secuencia.proximo_numero += 1
    secuencia.updated_at = datetime.utcnow()
    
    # NO hacer commit aquí - se hará en la transacción principal
    # El lock se libera cuando la transacción padre hace commit
    
    # 4. Retornar formateado
    return str(numero_actual).zfill(8)


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
        igv_pct = Decimal(str(producto.igv_porcentaje or 18))
        
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
    # Determinar tipo_documento según la serie
    # F=Factura(01), B=Boleta(03), NC=Nota Crédito(07), ND=Nota Débito(08)
    if serie.startswith("NC"):
        tipo_documento = "07"
    elif serie.startswith("ND"):
        tipo_documento = "08"
    elif serie.startswith("B"):
        tipo_documento = "03"
    else:
        tipo_documento = "01"  # Default: Factura
    numero_comprobante = await obtener_siguiente_numero_comprobante(db, serie, tipo_documento)
    
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


async def obtener_factura(db: AsyncSession, factura_id: int) -> Factura:
    query = select(Factura).where(Factura.id == factura_id, Factura.deleted_at == None)
    result = await db.execute(query)
    factura = result.scalar_one_or_none()
    
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    return factura


async def obtener_items_factura(db: AsyncSession, factura_id: int) -> list[ItemFactura]:
    query = select(ItemFactura).where(ItemFactura.factura_id == factura_id)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return items


async def eliminar_factura(db: AsyncSession, factura_id: int):
    query = select(Factura).where(Factura.id == factura_id, Factura.deleted_at == None)
    result = await db.execute(query)
    factura = result.scalar_one_or_none()
    
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # Solo se puede eliminar facturas en estado borrador
    if factura.estado != "borrador":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar una factura en estado '{factura.estado}'. Solo se pueden eliminar facturas en estado 'borrador'."
        )
    
    factura.deleted_at = datetime.now()
    await db.commit()
    
    return factura


async def editar_factura(db: AsyncSession, factura_id: int, data: CreateFacturaRequest) -> Factura:
    """
    Edita una factura existente. Solo permite edición si está en estado 'borrador'.
    Actualiza tanto los campos de la factura como sus items.
    """
    
    # 1. Obtener factura existente
    query = select(Factura).where(Factura.id == factura_id, Factura.deleted_at == None)
    result = await db.execute(query)
    factura = result.scalar_one_or_none()
    
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # 2. Validar estado borrador
    if factura.estado != "borrador":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede editar una factura en estado '{factura.estado}'. Solo se pueden editar facturas en estado 'borrador'."
        )
    
    # 3. Validar cliente
    cliente = await db.execute(
        select(Cliente).where(Cliente.id == data.cliente_id)
    )
    cliente = cliente.scalar_one_or_none()
    if not cliente:
        raise HTTPException(status_code=400, detail="Cliente no encontrado")
    
    # 4. Verificar si algún producto necesita conversión de moneda
    necesita_tc = False
    for item in data.items:
        producto = await db.execute(
            select(Producto).where(Producto.id == item.producto_id)
        )
        producto = producto.scalar_one_or_none()
        if not producto:
            raise HTTPException(status_code=400, detail=f"Producto con ID {item.producto_id} no encontrado")
        moneda_producto = producto.moneda or "PEN"
        
        if moneda_producto != data.moneda:
            necesita_tc = True
            break
    
    # 5. Obtener TC del día si es necesario
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
    
    # 6. Procesar items
    subtotal_factura = Decimal(0)
    igv_total_factura = Decimal(0)
    items_procesados = []
    
    for item in data.items:
        producto = await db.execute(
            select(Producto).where(Producto.id == item.producto_id)
        )
        producto = producto.scalar_one_or_none()
        
        # Conversión de moneda
        moneda_producto = producto.moneda or "PEN"
        precio_original = Decimal(str(producto.precio_unitario))
        cantidad = Decimal(str(item.cantidad))
        igv_pct = Decimal(str(producto.igv_porcentaje or 18))
        
        precio_en_factura = precio_original
        tc_usado = None
        
        if moneda_producto != data.moneda:
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
        
        # Cálculos del item
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
    
    # 7. Eliminar items anteriores
    items_query = select(ItemFactura).where(ItemFactura.factura_id == factura_id)
    items_result = await db.execute(items_query)
    items_anteriores = items_result.scalars().all()
    
    for item_anterior in items_anteriores:
        await db.delete(item_anterior)
    
    # Flush para asegurar que los items se eliminen antes de insertar nuevos
    await db.flush()
    
    # 8. Actualizar campos de la factura
    factura.cliente_id = data.cliente_id
    factura.moneda = data.moneda
    factura.tipo_cambio = tc_del_dia
    factura.numero_serie = data.numero_serie or factura.numero_serie
    factura.tipo_operacion = data.tipo_operacion or factura.tipo_operacion
    factura.forma_pago = data.forma_pago or factura.forma_pago
    factura.subtotal = subtotal_factura
    factura.igv_total = igv_total_factura
    factura.total = total_factura
    
    # 9. Crear nuevos items
    for item_data in items_procesados:
        nuevo_item = ItemFactura(
            factura_id=factura.id,
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
    await db.refresh(factura)
    
    return factura