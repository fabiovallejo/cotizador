def cotizacion_to_dict(c):
    return {
        "id_cotizacion": c.id_cotizacion,
        "codigo": c.codigo_cotizacion,
        "estado": c.estado,
        "id_cliente": c.id_cliente,
        "id_usuario": c.id_usuario,
        "fecha_creacion": c.fecha_creacion.isoformat(),

        "items": [
            cotizacion_item_to_dict(item)
            for item in c.items
        ],

        "subtotal": float(
            sum(item.subtotal for item in c.items)
        ),
        "total": float(
            sum(item.subtotal for item in c.items)
        )
    }


def cotizacion_item_to_dict(item):
    return {
        "id_producto": item.id_producto,
        "nombre_producto": item.nombre_producto,
        "precio_unitario": float(item.precio_unitario),
        "cantidad": item.cantidad,
        "subtotal": float(item.subtotal)
    }