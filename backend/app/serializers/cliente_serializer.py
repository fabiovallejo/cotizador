def cliente_to_dict(cliente):
    return {
        "id_cliente": cliente.id_cliente,
        "numero_documento": cliente.numero_documento,
        "nombre_o_razon_social": cliente.nombre_o_razon_social,
        "email": cliente.email,
        "telefono": cliente.telefono,
        "direccion": cliente.direccion,
        "esta_activo": cliente.esta_activo
    }
