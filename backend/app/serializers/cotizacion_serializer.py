def cotizacion_item_to_dict(item):
    return {
        "id_producto": item.id_producto,
        "nombre_producto": item.nombre_producto,
        "precio_unitario": float(item.precio_unitario),
        "cantidad": item.cantidad,
        "subtotal": float(item.subtotal)
    }

def cotizacion_resumen_to_dict(c):
    return {
        "id_cotizacion": c.id_cotizacion,
        "codigo": c.codigo_cotizacion,
        "estado": c.estado,
        "total": float(c.total),
        "fecha_creacion": c.fecha_creacion.isoformat()
    }

def cotizacion_detalle_to_dict(cotizacion, items):
    return {
        "id_cotizacion": cotizacion.id_cotizacion,
        "codigo": cotizacion.codigo_cotizacion,
        "estado": cotizacion.estado,
        "id_cliente": cotizacion.id_cliente,
        "id_usuario": cotizacion.id_usuario,
        "fecha_creacion": cotizacion.fecha_creacion.isoformat(),
        "subtotal": float(cotizacion.subtotal),
        "total": float(cotizacion.total),
        "items": [cotizacion_item_to_dict(i) for i in items]
    }
