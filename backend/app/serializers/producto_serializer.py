def producto_to_dict(p):
    return {
        "id_producto": p.id_producto,
        "nombre": p.nombre,
        "sku": p.SKU,
        "precio": float(p.precio)
    }

