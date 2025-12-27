from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.cotizacion import Cotizacion
from app.models.cotizacion_item import CotizacionItem
from datetime import datetime
from app.serializers.cotizacion_serializer import cotizacion_to_dict

def generar_codigo_cotizacion():
    return f"COT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def listar_cotizaciones(db: Session, id_empresa: int):
    return (
        db.query(Cotizacion)
        .filter(Cotizacion.id_empresa == id_empresa)
        .order_by(Cotizacion.fecha_creacion.desc())
        .all()
    )

def crear_cotizacion(db: Session, id_empresa: int, id_usuario: int, id_cliente: int):
    cotizacion = Cotizacion(
        id_empresa=id_empresa,
        id_usuario=id_usuario,
        id_cliente=id_cliente,
        codigo_cotizacion=generar_codigo_cotizacion(),
        estado= "BORRADOR",
        subtotal=0,
        total=0
    )

    db.add(cotizacion)
    db.commit()
    db.refresh(cotizacion)

    return cotizacion

def obtener_cotizacion(db, id_cotizacion, id_empresa): 
    return (
        db.query(Cotizacion)
        .filter(
            Cotizacion.id_cotizacion == id_cotizacion,
            Cotizacion.id_empresa == id_empresa
        )
        .first()
    )

def cerrar_cotizacion(db, id_cotizacion, id_empresa):
    cotizacion = (
        db.query(Cotizacion)
        .filter(
            Cotizacion.id_cotizacion == id_cotizacion,
            Cotizacion.id_empresa == id_empresa
        )
        .first()
    )

    if not cotizacion:
        return None, "NO_EXISTE"

    if cotizacion.estado != "BORRADOR":
        return None, "YA_CERRADA"

    items = (
        db.query(CotizacionItem)
        .filter(CotizacionItem.id_cotizacion == id_cotizacion)
        .count()
    )

    if items == 0:
        return None, "SIN_ITEMS"

    cotizacion.estado = "CERRADA"
    cotizacion.fecha_cierre = datetime.utcnow()

    db.commit()
    db.refresh(cotizacion)

    return cotizacion, None

def recalcular_totales(db, id_cotizacion):
    subtotal = (
        db.query(func.coalesce(func.sum(CotizacionItem.subtotal), 0))
        .filter(CotizacionItem.id_cotizacion == id_cotizacion)
        .scalar()
    )

    cotizacion = (
        db.query(Cotizacion)
        .filter(Cotizacion.id_cotizacion == id_cotizacion)
        .first()
    )

    if cotizacion:
        cotizacion.subtotal = subtotal
        cotizacion.total = subtotal
        db.commit()
