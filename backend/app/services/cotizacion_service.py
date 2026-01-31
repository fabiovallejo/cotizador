from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from fastapi import HTTPException, status
from typing import Optional
from app.services.tipo_cambio_service import tipo_cambio_service

from app.models.tenant import Cotizacion, ItemCotizacion, Cliente, Producto, Factura, ItemFactura
from app.schemas.cotizacion import CreateCotizacionRequest
import logging

logger = logging.getLogger(__name__)


async def obtener_siguiente_numero_cotizacion(db: AsyncSession) -> str:
    """
    Genera el siguiente número de cotización.
    Formato: COT-YYYY-NNN
    """
    year = datetime.now().year
    prefix = f"COT-{year}-"
    
    result = await db.execute(
        select(func.max(Cotizacion.numero_cotizacion))
        .where(Cotizacion.numero_cotizacion.like(f"{prefix}%"))
    )
    max_numero = result.scalar_one_or_none()
    
    if max_numero:
        # Extraer el número secuencial
        try:
            ultimo_numero = int(max_numero.split("-")[-1])
            siguiente = ultimo_numero + 1
        except ValueError:
            siguiente = 1
    else:
        siguiente = 1
    
    return f"{prefix}{str(siguiente).zfill(3)}"


async def crear_cotizacion(
    db: AsyncSession,
    data: CreateCotizacionRequest,
    usuario_id: int
) -> Cotizacion:
    """
    Crea una nueva cotización con sus items.
    """
    # 1. Validar cliente
    cliente = await db.execute(
        select(Cliente).where(Cliente.id == data.cliente_id)
    )
    cliente = cliente.scalar_one_or_none()
    if not cliente:
        raise HTTPException(status_code=400, detail="Cliente no encontrado")
    
    # 2. Verificar si algún producto necesita conversión de moneda
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
    
    # 3. Obtener TC del día si es necesario
    tc_del_dia = None
    if necesita_tc:
        try:
            tc_data = await tipo_cambio_service.obtener_tc_del_dia()
            tc_del_dia = Decimal(tc_data["venta"])
            logger.info(f"TC {data.moneda}: {tc_del_dia}")
        except Exception as e:
            logger.error(f"Error obteniendo TC: {e}")
            raise HTTPException(
                status_code=500,
                detail="No se pudo obtener TC automático de SUNAT"
            )
    
    # 4. Procesar items con conversión
    subtotal_cotizacion = Decimal(0)
    igv_total_cotizacion = Decimal(0)
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
        
        precio_en_cotizacion = precio_original
        
        if moneda_producto != data.moneda:
            if data.moneda == "PEN":
                # Convertir a PEN (producto está en USD)
                if not tc_del_dia:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No hay TC para convertir {moneda_producto} a {data.moneda}"
                    )
                precio_en_cotizacion = precio_original * tc_del_dia
            elif moneda_producto == "PEN" and data.moneda != "PEN":
                # Convertir de PEN a USD
                if not tc_del_dia:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No hay TC para convertir {moneda_producto} a {data.moneda}"
                    )
                precio_en_cotizacion = precio_original / tc_del_dia
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Conversión {moneda_producto} a {data.moneda} no soportada"
                )
        
        # Cálculos del item
        subtotal_item = precio_en_cotizacion * cantidad
        igv_item = subtotal_item * igv_pct / Decimal(100)
        total_item = subtotal_item + igv_item
        
        subtotal_cotizacion += subtotal_item
        igv_total_cotizacion += igv_item
        
        items_procesados.append({
            "producto_id": producto.id,
            "precio_unitario": precio_en_cotizacion,
            "cantidad": cantidad,
            "igv_porcentaje": igv_pct,
            "igv_monto": igv_item,
            "subtotal": subtotal_item,
            "total": total_item,
        })
    
    total_cotizacion = subtotal_cotizacion + igv_total_cotizacion
    
    # 5. Generar número de cotización
    numero_cotizacion = await obtener_siguiente_numero_cotizacion(db)
    
    # 6. Calcular fecha de vencimiento
    fecha_vencimiento = datetime.now().date() + timedelta(days=data.vigencia_dias)
    
    # 7. Crear cotización
    nueva_cotizacion = Cotizacion(
        numero_cotizacion=numero_cotizacion,
        cliente_id=data.cliente_id,
        usuario_id=usuario_id,
        moneda=data.moneda,
        tipo_cambio=tc_del_dia,
        subtotal=subtotal_cotizacion,
        descuento_total=Decimal(0),
        igv_total=igv_total_cotizacion,
        total=total_cotizacion,
        estado="borrador",
        vigencia_dias=data.vigencia_dias,
        fecha_vencimiento=fecha_vencimiento,
        notas_internas=data.notas_internas,
        terminos_condiciones=data.terminos_condiciones,
    )
    
    db.add(nueva_cotizacion)
    await db.flush()
    
    # 8. Crear items
    for item_data in items_procesados:
        nuevo_item = ItemCotizacion(
            cotizacion_id=nueva_cotizacion.id,
            producto_id=item_data["producto_id"],
            cantidad=item_data["cantidad"],
            precio_unitario=item_data["precio_unitario"],
            igv_porcentaje=item_data["igv_porcentaje"],
            igv_monto=item_data["igv_monto"],
            subtotal=item_data["subtotal"],
            total=item_data["total"],
        )
        db.add(nuevo_item)
    
    await db.commit()
    await db.refresh(nueva_cotizacion)
    
    return nueva_cotizacion


async def listar_cotizaciones(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    estado: Optional[str] = None,
    busqueda: Optional[str] = None,
) -> list[Cotizacion]:
    """
    Lista cotizaciones con filtros y paginación.
    """
    query = select(Cotizacion).where(Cotizacion.deleted_at == None)
    
    if estado:
        query = query.where(Cotizacion.estado == estado)
    
    if busqueda:
        query = query.where(
            or_(
                Cotizacion.numero_cotizacion.ilike(f"%{busqueda}%"),
                Cotizacion.cliente.has(
                    Cliente.razon_social.ilike(f"%{busqueda}%")
                ),
                Cotizacion.cliente.has(
                    Cliente.numero_documento.ilike(f"%{busqueda}%")
                ),
            )
        )
    
    query = query.order_by(Cotizacion.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    cotizaciones = result.scalars().all()
    
    return cotizaciones


async def obtener_cotizacion(db: AsyncSession, cotizacion_id: int) -> Cotizacion:
    """
    Obtiene una cotización por ID.
    """
    query = select(Cotizacion).where(
        Cotizacion.id == cotizacion_id, 
        Cotizacion.deleted_at == None
    )
    result = await db.execute(query)
    cotizacion = result.scalar_one_or_none()
    
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    return cotizacion


async def obtener_items_cotizacion(db: AsyncSession, cotizacion_id: int) -> list[ItemCotizacion]:
    """
    Obtiene los items de una cotización.
    """
    query = select(ItemCotizacion).where(ItemCotizacion.cotizacion_id == cotizacion_id)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return items


async def editar_cotizacion(
    db: AsyncSession, 
    cotizacion_id: int, 
    data: CreateCotizacionRequest
) -> Cotizacion:
    """
    Edita una cotización. Solo permite edición si está en estado 'borrador'.
    """
    
    # 1. Obtener cotización
    query = select(Cotizacion).where(
        Cotizacion.id == cotizacion_id, 
        Cotizacion.deleted_at == None
    )
    result = await db.execute(query)
    cotizacion = result.scalar_one_or_none()
    
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    # 2. Validar estado
    if cotizacion.estado != "borrador":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede editar una cotización en estado '{cotizacion.estado}'. Solo se pueden editar cotizaciones en estado 'borrador'."
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
            raise HTTPException(
                status_code=500,
                detail="No se pudo obtener TC automático de SUNAT"
            )
    
    # 6. Procesar items con conversión
    subtotal_cotizacion = Decimal(0)
    igv_total_cotizacion = Decimal(0)
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
        
        precio_en_cotizacion = precio_original
        
        if moneda_producto != data.moneda:
            if data.moneda == "PEN":
                # Convertir a PEN (producto está en USD)
                if not tc_del_dia:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No hay TC para convertir {moneda_producto} a {data.moneda}"
                    )
                precio_en_cotizacion = precio_original * tc_del_dia
            elif moneda_producto == "PEN" and data.moneda != "PEN":
                # Convertir de PEN a USD
                if not tc_del_dia:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No hay TC para convertir {moneda_producto} a {data.moneda}"
                    )
                precio_en_cotizacion = precio_original / tc_del_dia
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Conversión {moneda_producto} a {data.moneda} no soportada"
                )
        
        # Cálculos del item
        subtotal_item = precio_en_cotizacion * cantidad
        igv_item = subtotal_item * igv_pct / Decimal(100)
        total_item = subtotal_item + igv_item
        
        subtotal_cotizacion += subtotal_item
        igv_total_cotizacion += igv_item
        
        items_procesados.append({
            "producto_id": producto.id,
            "precio_unitario": precio_en_cotizacion,
            "cantidad": cantidad,
            "igv_porcentaje": igv_pct,
            "igv_monto": igv_item,
            "subtotal": subtotal_item,
            "total": total_item,
        })
    
    total_cotizacion = subtotal_cotizacion + igv_total_cotizacion
    
    # 7. Eliminar items anteriores
    items_query = select(ItemCotizacion).where(ItemCotizacion.cotizacion_id == cotizacion_id)
    items_result = await db.execute(items_query)
    items_anteriores = items_result.scalars().all()
    
    for item_anterior in items_anteriores:
        await db.delete(item_anterior)
    
    await db.flush()
    
    # 8. Actualizar cotización
    cotizacion.cliente_id = data.cliente_id
    cotizacion.moneda = data.moneda
    cotizacion.tipo_cambio = tc_del_dia
    cotizacion.vigencia_dias = data.vigencia_dias
    cotizacion.fecha_vencimiento = datetime.now().date() + timedelta(days=data.vigencia_dias)
    cotizacion.notas_internas = data.notas_internas
    cotizacion.terminos_condiciones = data.terminos_condiciones
    cotizacion.subtotal = subtotal_cotizacion
    cotizacion.igv_total = igv_total_cotizacion
    cotizacion.total = total_cotizacion
    
    # 9. Crear nuevos items
    for item_data in items_procesados:
        nuevo_item = ItemCotizacion(
            cotizacion_id=cotizacion.id,
            producto_id=item_data["producto_id"],
            cantidad=item_data["cantidad"],
            precio_unitario=item_data["precio_unitario"],
            igv_porcentaje=item_data["igv_porcentaje"],
            igv_monto=item_data["igv_monto"],
            subtotal=item_data["subtotal"],
            total=item_data["total"],
        )
        db.add(nuevo_item)
    
    await db.commit()
    await db.refresh(cotizacion)
    
    return cotizacion


async def eliminar_cotizacion(db: AsyncSession, cotizacion_id: int) -> Cotizacion:
    """
    Elimina (soft delete) una cotización. Solo permite si está en estado 'borrador'.
    """
    query = select(Cotizacion).where(
        Cotizacion.id == cotizacion_id, 
        Cotizacion.deleted_at == None
    )
    result = await db.execute(query)
    cotizacion = result.scalar_one_or_none()
    
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    if cotizacion.estado != "borrador":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar una cotización en estado '{cotizacion.estado}'. Solo se pueden eliminar cotizaciones en estado 'borrador'."
        )
    
    cotizacion.deleted_at = datetime.now()
    await db.commit()
    
    return cotizacion


async def convertir_a_factura(
    db: AsyncSession, 
    cotizacion_id: int,
    usuario_id: int
) -> dict:
    """
    Convierte una cotización a factura.
    Solo permite conversión si estado = 'aceptada' o 'borrador'.
    Valida que cliente y productos no estén en soft delete.
    """
    from sqlalchemy import Integer
    
    # 1. Obtener cotización (no eliminada)
    query = select(Cotizacion).where(
        Cotizacion.id == cotizacion_id, 
        Cotizacion.deleted_at == None
    )
    result = await db.execute(query)
    cotizacion = result.scalar_one_or_none()
    
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada o fue eliminada")
    
    # 2. Validar estado (solo aceptada o borrador)
    estados_permitidos = ["aceptada", "borrador"]
    if cotizacion.estado not in estados_permitidos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se pueden convertir cotizaciones en estado 'aceptada' o 'borrador'. Estado actual: '{cotizacion.estado}'."
        )
    
    # 3. Verificar que no haya sido convertida antes
    if cotizacion.convertida_a_factura_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta cotización ya fue convertida a factura."
        )
    
    # 4. Validar que el cliente no esté eliminado
    cliente_query = select(Cliente).where(
        Cliente.id == cotizacion.cliente_id,
        Cliente.deleted_at == None
    )
    cliente_result = await db.execute(cliente_query)
    cliente = cliente_result.scalar_one_or_none()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El cliente de esta cotización fue eliminado. No se puede convertir."
        )
    
    # 5. Obtener items de la cotización
    items_query = select(ItemCotizacion).where(ItemCotizacion.cotizacion_id == cotizacion_id)
    items_result = await db.execute(items_query)
    items_cotizacion = items_result.scalars().all()
    
    if not items_cotizacion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cotización no tiene items. No se puede convertir."
        )
    
    # 6. Validar que todos los productos no estén eliminados
    for item_cot in items_cotizacion:
        producto_query = select(Producto).where(
            Producto.id == item_cot.producto_id,
            Producto.deleted_at == None
        )
        producto_result = await db.execute(producto_query)
        producto = producto_result.scalar_one_or_none()
        
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El producto ID {item_cot.producto_id} fue eliminado. No se puede convertir."
            )
    
    # 7. Generar número de comprobante para la factura
    serie = "F001"
    result = await db.execute(
        select(func.max(func.cast(Factura.numero_comprobante, Integer)))
        .where(Factura.numero_serie == serie)
    )
    max_numero = result.scalar_one_or_none()
    siguiente = (max_numero or 0) + 1
    numero_comprobante = str(siguiente).zfill(8)
    
    # 8. Crear factura con datos de la cotización
    nueva_factura = Factura(
        numero_serie=serie,
        numero_comprobante=numero_comprobante,
        cliente_id=cotizacion.cliente_id,
        usuario_id=usuario_id,
        cotizacion_id=cotizacion.id,
        tipo_comprobante="01",
        tipo_operacion="0101",
        moneda=cotizacion.moneda,
        tipo_cambio=cotizacion.tipo_cambio,
        subtotal=cotizacion.subtotal,
        descuento_total=cotizacion.descuento_total,
        igv_total=cotizacion.igv_total,
        total=cotizacion.total,
        fecha_emision=datetime.now().date(),
        hora_emision=datetime.now().time(),
        forma_pago="Contado",
        estado="borrador",
    )
    
    db.add(nueva_factura)
    await db.flush()
    
    # 9. Copiar items a la factura (precios CONGELADOS de la cotización)
    for item_cot in items_cotizacion:
        # Obtener producto para moneda_original
        producto = await db.execute(
            select(Producto).where(Producto.id == item_cot.producto_id)
        )
        producto = producto.scalar_one_or_none()
        
        nuevo_item = ItemFactura(
            factura_id=nueva_factura.id,
            producto_id=item_cot.producto_id,
            cantidad=item_cot.cantidad,
            # Precio CONGELADO de la cotización
            precio_unitario=item_cot.precio_unitario,
            precio_en_factura=item_cot.precio_unitario,
            # Datos de conversión originales
            moneda_original=producto.moneda if producto else "PEN",
            precio_original=item_cot.precio_unitario,
            tipo_cambio_usado=cotizacion.tipo_cambio,
            # IGV calculado sobre precio congelado
            igv_porcentaje=item_cot.igv_porcentaje,
            igv_monto=item_cot.igv_monto,
            subtotal=item_cot.subtotal,
            total=item_cot.total,
            tipo_afectacion_igv="10",
        )
        db.add(nuevo_item)
    
    # 10. Actualizar cotización
    cotizacion.estado = "convertida"
    cotizacion.convertida_a_factura_id = nueva_factura.id
    
    # Guardar IDs antes del commit (después del commit los objetos expiran)
    cotizacion_id = cotizacion.id
    factura_id = nueva_factura.id
    numero_factura = f"{serie}-{numero_comprobante}"
    
    await db.commit()
    
    # 11. Retornar respuesta específica
    return {
        "cotizacion_id": cotizacion_id,
        "factura_id": factura_id,
        "numero_factura": numero_factura,
        "mensaje": "Cotización convertida a factura exitosamente"
    }
