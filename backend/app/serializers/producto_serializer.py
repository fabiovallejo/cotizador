def producto_to_dict(producto):
    return {
        "id_producto": producto.id_producto,
        "SKU": producto.SKU,
        "nombre": producto.nombre,
        "precio": float(producto.precio),
        "descripcion": producto.descripcion,
        "id_empresa": producto.id_empresa,
        "esta_activo": producto.esta_activo
    }
