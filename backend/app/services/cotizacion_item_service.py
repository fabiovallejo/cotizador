from app.models.cotizacion_item import CotizacionItem
from app.models.producto import Producto
from app.models.cotizacion import Cotizacion

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
