ROLES_DISPONIBLES = {
    "admin": {
        "nombre": "Administrador",
        "descripcion": "Control total del sistema",
        "permisos": [
            # Usuarios
            "usuarios:crear",
            "usuarios:leer",
            "usuarios:editar",
            "usuarios:eliminar",
            "usuarios:cambiar_rol",
            
            # Empresa
            "empresa:editar",
            "empresa:ver_certificado",
            "empresa:cambiar_ambiente_sunat",
            
            # Reportes
            "reportes:ver_todo",
            
            # Auditoría
            "auditoria:ver",
        ]
    },
    
    "contador": {
        "nombre": "Contador/Especialista Fiscal",
        "descripcion": "Gestiona aspectos fiscales y de auditoría",
        "permisos": [
            # Cotizaciones - Solo lectura
            "cotizaciones:leer",
            
            # Facturas - Solo lectura
            "facturas:leer",
            "facturas:ver_xml",
            "facturas:descargar_pdf",
            
            # Notas de crédito - Lectura
            "notas:leer",
            
            # Reportes
            "reportes:ver_fiscal",
            "reportes:ver_contable",
            "reportes:exportar",
            
            # Auditoría
            "auditoria:ver",
        ]
    },
    
    "gerente_ventas": {
        "nombre": "Gerente de Ventas",
        "descripcion": "Supervisa vendedores y operaciones de venta",
        "permisos": [
            # Clientes
            "clientes:crear",
            "clientes:leer",
            "clientes:editar",
            
            # Productos
            "productos:leer",
            
            # Cotizaciones
            "cotizaciones:crear",
            "cotizaciones:leer",
            "cotizaciones:editar",
            "cotizaciones:eliminar",
            "cotizaciones:convertir_factura",
            
            # Facturas
            "facturas:leer",
            "facturas:descargar_pdf",
            
            # Reportes
            "reportes:ver_ventas",
            "reportes:ver_cliente",
            "reportes:exportar",
        ]
    },
    
    "vendedor": {
        "nombre": "Vendedor",
        "descripcion": "Crea cotizaciones y facturas de venta",
        "permisos": [
            # Clientes
            "clientes:crear",
            "clientes:leer",
            "clientes:editar",
            
            # Productos
            "productos:leer",
            
            # Cotizaciones
            "cotizaciones:crear",
            "cotizaciones:leer",
            "cotizaciones:editar",  # Solo propias
            "cotizaciones:convertir_factura",
            
            # Facturas
            "facturas:crear",
            "facturas:leer",
            "facturas:descargar_pdf",
            "facturas:enviar_sunat",  # Trigger emisión
            
            # Reportes
            "reportes:ver_propias",
        ]
    },
    
    "operario": {
        "nombre": "Operario/Asistente",
        "descripcion": "Soporte operativo básico",
        "permisos": [
            # Clientes
            "clientes:leer",
            "clientes:crear",  # Contactos básicos
            
            # Productos
            "productos:leer",
            
            # Cotizaciones
            "cotizaciones:leer",
            
            # Facturas
            "facturas:leer",
            "facturas:descargar_pdf",
        ]
    },
    "readonly": {
        "nombre": "Solo Lectura",
        "descripcion": "Acceso de visualización sin edición",
        "permisos": [
            "productos:leer",
            "clientes:leer",
            "cotizaciones:leer",
            "facturas:leer",
            "reportes:ver_todo",
        ]
    }
}

# ============================================================================
# MAPEO DE PERMISOS POR ROL
# ============================================================================

PERMISOS_POR_ROL = {rol: config["permisos"] for rol, config in ROLES_DISPONIBLES.items()}