"""
Módulo de reportes de negocio.

Endpoints para generar reportes agregados:
- Cotizaciones: métricas de conversión, montos, pendientes, alertas
- Productos Top: ranking por ingresos con margen y tasa conversión por producto
- Clientes: análisis de clientes con segmentación VIP/Regular, inactivos, alertas
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, desc, and_
from typing import Optional
from datetime import date, datetime, timedelta

from app.core.dependencies import get_current_user, get_tenant_db, CurrentUser
from app.models.tenant import Cotizacion, ItemCotizacion, Producto, Cliente
from app.models.shared import Usuario

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])


# ============================================================================
# REPORTE 1: COTIZACIONES
# ============================================================================

@router.get(
    "/cotizaciones",
    summary="Reporte de cotizaciones",
    description="Métricas agregadas y detalle de cotizaciones en un período."
)
async def reporte_cotizaciones(
    fecha_inicio: date = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    fecha_fin: date = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    vendedor_id: Optional[int] = Query(None, description="Filtrar por vendedor"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    fecha_inicio_dt = datetime.combine(fecha_inicio, datetime.min.time())
    fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time())
    
    filters = [
        Cotizacion.created_at >= fecha_inicio_dt,
        Cotizacion.created_at <= fecha_fin_dt,
        Cotizacion.deleted_at.is_(None),
    ]
    if vendedor_id:
        filters.append(Cotizacion.usuario_id == vendedor_id)
    if cliente_id:
        filters.append(Cotizacion.cliente_id == cliente_id)

    umbral_pendiente = datetime.utcnow() - timedelta(days=7)

    # Métricas agregadas
    metricas_query = select(
        func.count(Cotizacion.id).label("total_cotizaciones"),
        func.coalesce(func.sum(Cotizacion.total), 0).label("monto_total"),
        func.count(case((Cotizacion.estado == "aceptada", 1))).label("aceptadas"),
        func.count(case((Cotizacion.estado == "convertida", 1))).label("convertidas"),
        func.count(case((Cotizacion.estado == "rechazada", 1))).label("rechazadas"),
        # Pendientes: borrador o enviada sin respuesta por >7 días
        func.count(case((
            and_(
                Cotizacion.estado.in_(["borrador", "enviada"]),
                Cotizacion.created_at <= umbral_pendiente,
            ), 1
        ))).label("pendientes"),
        # Monto de rechazadas
        func.coalesce(func.sum(case(
            (Cotizacion.estado == "rechazada", Cotizacion.total),
            else_=0
        )), 0).label("monto_rechazado"),
        # Monto de pendientes (borrador/enviada >7 días)
        func.coalesce(func.sum(case(
            (and_(
                Cotizacion.estado.in_(["borrador", "enviada"]),
                Cotizacion.created_at <= umbral_pendiente,
            ), Cotizacion.total),
            else_=0
        )), 0).label("monto_pendiente"),
    ).where(and_(*filters))

    result = await db.execute(metricas_query)
    row = result.one()
    
    total = row.total_cotizaciones or 0
    aceptadas = row.aceptadas or 0
    convertidas = row.convertidas or 0
    rechazadas = row.rechazadas or 0
    pendientes = row.pendientes or 0
    monto_total = float(row.monto_total or 0)
    monto_rechazado = float(row.monto_rechazado or 0)
    monto_pendiente = float(row.monto_pendiente or 0)

    metricas = {
        "total_cotizaciones": total,
        "monto_total": round(monto_total, 2),
        "porcentaje_aceptadas": round((aceptadas / total * 100) if total > 0 else 0, 1),
        "tasa_conversion": round((convertidas / total * 100) if total > 0 else 0, 1),
        "valor_promedio": round(monto_total / total if total > 0 else 0, 2),
        "tasa_rechazo": round((rechazadas / total * 100) if total > 0 else 0, 1),
        "pendientes": pendientes,
        "monto_perdido": round(monto_rechazado + monto_pendiente, 2),
    }

    # Alertas
    alertas = []
    if pendientes > 0:
        alertas.append({
            "tipo": "warning",
            "mensaje": f"{pendientes} cotización(es) sin respuesta hace más de 7 días",
        })
    if metricas["tasa_rechazo"] > 30:
        alertas.append({
            "tipo": "danger",
            "mensaje": f"Tasa de rechazo alta: {metricas['tasa_rechazo']}%",
        })
    if monto_rechazado + monto_pendiente > 0:
        alertas.append({
            "tipo": "info",
            "mensaje": f"Monto en riesgo: S/ {round(monto_rechazado + monto_pendiente, 2):,.2f}",
        })

    # Detalle
    detalle_query = (
        select(Cotizacion, Cliente.razon_social)
        .join(Cliente, Cotizacion.cliente_id == Cliente.id)
        .where(and_(*filters))
        .order_by(desc(Cotizacion.created_at))
    )
    detalle_result = await db.execute(detalle_query)
    rows = detalle_result.all()

    vendedor_ids = list({r[0].usuario_id for r in rows if r[0].usuario_id})
    vendedores_map = {}
    if vendedor_ids:
        vend_result = await db.execute(
            select(Usuario.id, Usuario.nombre, Usuario.apellido)
            .where(Usuario.id.in_(vendedor_ids))
        )
        for v in vend_result.all():
            vendedores_map[v.id] = f"{v.nombre} {v.apellido or ''}".strip()

    detalle = []
    for cot, cliente_nombre in rows:
        detalle.append({
            "id": cot.id,
            "numero": cot.numero_cotizacion,
            "cliente": cliente_nombre,
            "vendedor": vendedores_map.get(cot.usuario_id, "—"),
            "total": float(cot.total or 0),
            "moneda": cot.moneda or "PEN",
            "estado": cot.estado,
            "fecha": cot.created_at.strftime("%Y-%m-%d") if cot.created_at else "",
        })

    return {"metricas": metricas, "alertas": alertas, "detalle": detalle}


# ============================================================================
# REPORTE 2: PRODUCTOS TOP
# ============================================================================

@router.get(
    "/productos-top",
    summary="Reporte de productos más vendidos",
    description="Ranking de productos por ingresos en cotizaciones del período."
)
async def reporte_productos_top(
    fecha_inicio: date = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    fecha_fin: date = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    fecha_inicio_dt = datetime.combine(fecha_inicio, datetime.min.time())
    fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time())

    base_filters = [
        Cotizacion.created_at >= fecha_inicio_dt,
        Cotizacion.created_at <= fecha_fin_dt,
        Cotizacion.deleted_at.is_(None),
    ]

    # Query con métricas de conversión por producto
    query = (
        select(
            Producto.id,
            Producto.codigo,
            Producto.nombre,
            Producto.precio_unitario,
            Producto.costo_unitario,
            func.coalesce(func.sum(ItemCotizacion.cantidad), 0).label("cantidad_vendida"),
            func.coalesce(func.sum(ItemCotizacion.total), 0).label("ingresos"),
            # Total de cotizaciones donde aparece el producto
            func.count(func.distinct(Cotizacion.id)).label("total_cotizaciones_producto"),
            # Cotizaciones aceptadas o convertidas donde aparece
            func.count(func.distinct(case(
                (Cotizacion.estado.in_(["aceptada", "convertida"]), Cotizacion.id),
            ))).label("cotizaciones_cerradas"),
            # Monto en cotizaciones no aceptadas (rechazadas/pendientes)
            func.coalesce(func.sum(case(
                (Cotizacion.estado.in_(["rechazada", "borrador", "enviada"]), ItemCotizacion.total),
                else_=0
            )), 0).label("monto_no_cerrado"),
        )
        .join(ItemCotizacion, Producto.id == ItemCotizacion.producto_id)
        .join(Cotizacion, ItemCotizacion.cotizacion_id == Cotizacion.id)
        .where(and_(*base_filters))
        .group_by(Producto.id, Producto.codigo, Producto.nombre, Producto.precio_unitario, Producto.costo_unitario)
        .order_by(desc("ingresos"))
    )

    result = await db.execute(query)
    rows = result.all()

    total_ingresos = sum(float(r.ingresos or 0) for r in rows)

    productos = []
    alertas = []
    for r in rows:
        ingresos = float(r.ingresos or 0)
        precio = float(r.precio_unitario or 0)
        costo = float(r.costo_unitario or 0)
        cantidad = float(r.cantidad_vendida or 0)
        margen = round((precio - costo) * cantidad, 2) if costo > 0 else None
        total_cot_prod = r.total_cotizaciones_producto or 0
        cerradas = r.cotizaciones_cerradas or 0
        tasa_conv = round((cerradas / total_cot_prod * 100) if total_cot_prod > 0 else 0, 1)
        monto_no_cerrado = float(r.monto_no_cerrado or 0)
        
        productos.append({
            "id": r.id,
            "codigo": r.codigo,
            "nombre": r.nombre,
            "cantidad_vendida": round(cantidad, 2),
            "ingresos": round(ingresos, 2),
            "porcentaje_total": round(ingresos / total_ingresos * 100 if total_ingresos > 0 else 0, 1),
            "margen": margen,
            "tasa_conversion": tasa_conv,
            "total_cotizaciones": total_cot_prod,
            "cotizaciones_cerradas": cerradas,
            "monto_no_cerrado": round(monto_no_cerrado, 2),
        })

        # Alerta: producto con baja conversión pero alto volumen
        if tasa_conv < 50 and total_cot_prod >= 3:
            alertas.append({
                "tipo": "warning",
                "producto": r.nombre,
                "mensaje": f"\"{r.nombre}\" se cotiza frecuentemente pero solo cierra {tasa_conv}% de las veces. Monto sin cerrar: S/ {monto_no_cerrado:,.2f}",
            })

    return {
        "total_ingresos": round(total_ingresos, 2),
        "total_productos": len(productos),
        "productos": productos,
        "alertas": alertas,
    }


# ============================================================================
# REPORTE 3: CLIENTES
# ============================================================================

@router.get(
    "/clientes",
    summary="Reporte de clientes",
    description="Análisis de clientes con segmentación VIP/Regular."
)
async def reporte_clientes(
    fecha_inicio: date = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    fecha_fin: date = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    fecha_inicio_dt = datetime.combine(fecha_inicio, datetime.min.time())
    fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time())
    ahora = datetime.utcnow()

    # Query con todas las cotizaciones (no solo del período) para historial completo
    # pero filtrado por período para las métricas principales
    query = (
        select(
            Cliente.id,
            Cliente.razon_social,
            Cliente.numero_documento,
            Cliente.tipo_documento,
            func.count(Cotizacion.id).label("total_cotizaciones"),
            func.count(case((Cotizacion.estado == "aceptada", 1))).label("aceptadas"),
            func.coalesce(func.sum(Cotizacion.total), 0).label("monto_total"),
            func.max(Cotizacion.created_at).label("ultima_cotizacion"),
        )
        .join(Cotizacion, Cliente.id == Cotizacion.cliente_id)
        .where(
            Cotizacion.created_at >= fecha_inicio_dt,
            Cotizacion.created_at <= fecha_fin_dt,
            Cotizacion.deleted_at.is_(None),
        )
        .group_by(Cliente.id, Cliente.razon_social, Cliente.numero_documento, Cliente.tipo_documento)
        .order_by(desc("monto_total"))
    )

    result = await db.execute(query)
    rows = result.all()

    # También obtener la última cotización global (fuera del rango) para detectar inactivos
    global_ultima_query = (
        select(
            Cotizacion.cliente_id,
            func.max(Cotizacion.created_at).label("ultima_global"),
            func.coalesce(func.sum(Cotizacion.total), 0).label("monto_historico"),
        )
        .where(Cotizacion.deleted_at.is_(None))
        .group_by(Cotizacion.cliente_id)
    )
    global_result = await db.execute(global_ultima_query)
    global_map = {r.cliente_id: {"ultima": r.ultima_global, "monto_historico": float(r.monto_historico or 0)} for r in global_result.all()}

    montos = [float(r.monto_total or 0) for r in rows]
    promedio_global = sum(montos) / len(montos) if montos else 0
    umbral_vip = promedio_global * 2

    clientes = []
    alertas = []
    inactivos_count = 0

    for r in rows:
        monto = float(r.monto_total or 0)
        total_cot = r.total_cotizaciones or 0
        ticket_promedio = round(monto / total_cot if total_cot > 0 else 0, 2)
        segmento = "VIP" if monto >= umbral_vip else "Regular"

        # Calcular días desde última cotización global
        global_data = global_map.get(r.id, {})
        ultima_global = global_data.get("ultima")
        monto_historico = global_data.get("monto_historico", 0)
        dias_inactivo = (ahora - ultima_global).days if ultima_global else None
        es_inactivo = dias_inactivo is not None and dias_inactivo > 30

        if es_inactivo:
            inactivos_count += 1

        clientes.append({
            "id": r.id,
            "razon_social": r.razon_social,
            "numero_documento": r.numero_documento,
            "tipo_documento": r.tipo_documento,
            "total_cotizaciones": total_cot,
            "aceptadas": r.aceptadas or 0,
            "monto_total": round(monto, 2),
            "ticket_promedio": ticket_promedio,
            "ultima_cotizacion": r.ultima_cotizacion.strftime("%Y-%m-%d") if r.ultima_cotizacion else "",
            "segmento": segmento,
            "dias_inactivo": dias_inactivo,
            "monto_historico": round(monto_historico, 2),
            "es_inactivo": es_inactivo,
        })

        # Alerta para clientes VIP inactivos
        if es_inactivo and segmento == "VIP":
            alertas.append({
                "tipo": "danger",
                "mensaje": f"Cliente VIP perdido: \"{r.razon_social}\" — Hace {dias_inactivo} días sin cotización. Monto histórico: S/ {monto_historico:,.2f}",
            })
        elif es_inactivo:
            alertas.append({
                "tipo": "warning",
                "mensaje": f"Cliente inactivo: \"{r.razon_social}\" — Hace {dias_inactivo} días sin cotización",
            })

    return {
        "total_clientes": len(clientes),
        "promedio_global": round(promedio_global, 2),
        "umbral_vip": round(umbral_vip, 2),
        "inactivos": inactivos_count,
        "clientes": clientes,
        "alertas": alertas,
    }
