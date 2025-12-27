from app.models.cotizacion_item import CotizacionItem
from app.models.producto import Producto
from app.models.cotizacion import Cotizacion
from app.services.cotizacion_service import recalcular_totales

def agregar_item(db, id_cotizacion, payload):
    cotizacion = (
        db.query(Cotizacion)
        .filter(Cotizacion.id_cotizacion == id_cotizacion)
        .first()
    )

    if not cotizacion:
        return None

    producto = (
        db.query(Producto)
        .filter(Producto.id_producto == payload["id_producto"])
        .first()
    )

    if not producto:
        return None
    
    item_existente = (
    db.query(CotizacionItem)
    .filter(
        CotizacionItem.id_cotizacion == id_cotizacion,
        CotizacionItem.id_producto == payload["id_producto"]
    )
    .first()
    )

    cantidad = payload["cantidad"]

    if item_existente:
        item_existente.cantidad += cantidad
        item_existente.subtotal = (
            item_existente.cantidad * item_existente.precio_unitario
        )
        db.commit()
        db.refresh(item_existente)

        recalcular_totales(db, id_cotizacion)

        return item_existente, None

    precio = producto.precio
    subtotal = cantidad * precio

    item = CotizacionItem(
        id_cotizacion=id_cotizacion,
        id_producto=producto.id_producto,
        nombre_producto=producto.nombre,
        precio_unitario=precio,
        cantidad=cantidad,
        subtotal=subtotal
    )


    db.add(item)
    db.commit()
    db.refresh(item)

    return item, None

def actualizar_item(db, id_cotizacion, id_item, nueva_cantidad):
    if nueva_cantidad <= 0:
        return None, "CANTIDAD_INVALIDA"

    cotizacion = (
        db.query(Cotizacion)
        .filter(Cotizacion.id_cotizacion == id_cotizacion)
        .first()
    )

    if not cotizacion:
        return None, "NO_EXISTE"

    if cotizacion.estado == "CERRADA":
        return None, "COTIZACION_CERRADA"

    item = (
        db.query(CotizacionItem)
        .filter(
            CotizacionItem.id_cotizacionitem == id_item,
            CotizacionItem.id_cotizacion == id_cotizacion
        )
        .first()
    )

    if not item:
        return None, "ITEM_NO_EXISTE"

    item.cantidad = nueva_cantidad
    item.subtotal = item.precio_unitario * nueva_cantidad

    db.commit()
    db.refresh(item)

    return item, None

def eliminar_item(db, id_cotizacion, id_item):
    cotizacion = (
        db.query(Cotizacion)
        .filter(Cotizacion.id_cotizacion == id_cotizacion)
        .first()
    )

    if not cotizacion:
        return "NO_EXISTE"

    if cotizacion.estado == "CERRADA":
        return "COTIZACION_CERRADA"

    item = (
        db.query(CotizacionItem)
        .filter(
            CotizacionItem.id_cotizacionitem == id_item,
            CotizacionItem.id_cotizacion == id_cotizacion
        )
        .first()
    )

    if not item:
        return "ITEM_NO_EXISTE"

    db.delete(item)
    db.commit()

    return None

