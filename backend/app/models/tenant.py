"""
Modelos del SCHEMA TENANT (aislados por empresa).

Estos modelos están en schema="empresa_N".
Cada empresa tiene su PROPIO schema con sus propios datos.

IMPORTANTE: Los FKs a usuarios van a "public.usuarios.id"
Esto es cross-schema pero PostgreSQL lo soporta.
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Numeric, 
    ForeignKey, Index, UniqueConstraint, JSON, LargeBinary, Date, Time
)
from sqlalchemy.orm import relationship
from datetime import datetime, time as time_type

from app.models.base import Base, AuditMixin, SoftDeleteMixin

# ============================================================================
# TABLA: PRODUCTOS
# ============================================================================

class Producto(Base, AuditMixin):
    """
    Productos/servicios que la empresa vende.
    """
    __tablename__ = "productos"
    __table_args__ = (
        UniqueConstraint("codigo", name="uq_productos_codigo"),
        Index("idx_productos_codigo", "codigo"),
        Index("idx_productos_estado", "estado"),
        Index("idx_productos_categoria", "categoria"),
    )

    id = Column(Integer, primary_key=True)
    
    # ===== IDENTIFICACIÓN =====
    codigo = Column(String(100), unique=True, nullable=False)  # SKU
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String(1000))
    
    # ===== CÓDIGO SUNAT (OPCIONAL) =====
    # Ej: 50202500 = Bienes manufacturados
    codigo_unspsc = Column(String(8))
    
    # ===== CATEGORIZACIÓN =====
    tipo = Column(String(50), default="producto")  # producto | servicio | combo
    categoria = Column(String(100))
    marca = Column(String(100))
    
    # ===== PRECIOS =====
    precio_unitario = Column(Numeric(12, 4), nullable=False)
    costo_unitario = Column(Numeric(12, 4))
    precio_distribuidor = Column(Numeric(12, 4))
    
    # ===== IMPUESTOS =====
    aplica_igv = Column(Boolean, default=True)
    igv_porcentaje = Column(Integer, default=1800) 
    
    # ===== TIPO DE AFECTACIÓN IGV (SUNAT) =====
    # 10: Gravado - Operación Onerosa (18%)
    # 20: Exonerado (sin IGV)
    # 30: Inafecto (no aplica IGV - servicios especiales)
    # 40: Exportación
    tipo_afectacion_igv = Column(String(2), default="10")
    
    # ===== MONEDA =====
    moneda = Column(String(3), default="PEN")
    
    # ===== UNIDAD DE MEDIDA (SUNAT) =====
    # UND, DOC, CJA, KG, LTR, etc
    unidad_medida = Column(String(20), default="UND")
    
    # ===== STOCK =====
    tiene_stock = Column(Boolean, default=False)
    cantidad_stock = Column(Integer, default=0)
    
    # ===== ESTADO =====
    estado = Column(String(20), default="activo")  # activo | inactivo
    deleted_at = Column(DateTime)
    
    # ===== RELACIONES =====
    items_cotizacion = relationship("ItemCotizacion", back_populates="producto")
    items_factura = relationship("ItemFactura", back_populates="producto")
    
    def __repr__(self):
        return f"<Producto(codigo={self.codigo}, nombre={self.nombre})>"


# ============================================================================
# TABLA: CLIENTES
# ============================================================================

class Cliente(Base, AuditMixin):
    """
    Clientes a los que la empresa vende.
    Puede ser persona física (DNI) o jurídica (RUC).
    """
    __tablename__ = "clientes"
    __table_args__ = (
        UniqueConstraint("numero_documento", name="uq_clientes_numero_documento"),
        Index("idx_clientes_numero_documento", "numero_documento"),
        Index("idx_clientes_razon_social", "razon_social"),
        Index("idx_clientes_estado", "estado"),
    )

    id = Column(Integer, primary_key=True)
    
    # ===== IDENTIFICACIÓN (SUNAT) =====
    tipo_documento = Column(String(10), nullable=False)  # RUC | DNI | PASAPORTE | OTROS
    numero_documento = Column(String(15), unique=True, nullable=False)
    
    # ===== INFORMACIÓN =====
    razon_social = Column(String(255), nullable=False)
    nombre_comercial = Column(String(255))
    
    # ===== CONTACTO =====
    email = Column(String(255))
    telefono = Column(String(20))
    
    # ===== DIRECCIÓN (SUNAT REQUIERE) =====
    direccion_completa = Column(String(500))
    
    # ===== UBIGEO (Código SUNAT de ubicación geográfica) =====
    # Ej: 150131 = Lima, Lima, Lima
    ubigeo = Column(String(6))
    
    # ===== INFORMACIÓN ADICIONAL =====
    es_cliente_frecuente = Column(Boolean, default=False)
    
    # ===== ESTADO =====
    estado = Column(String(20), default="activo")  # activo | inactivo
    deleted_at = Column(DateTime)
    
    # ===== RELACIONES =====
    cotizaciones = relationship("Cotizacion", back_populates="cliente")
    facturas = relationship("Factura", back_populates="cliente")
    
    def __repr__(self):
        return f"<Cliente(numero_documento={self.numero_documento}, razon_social={self.razon_social})>"


# ============================================================================
# TABLA: COTIZACIONES
# ============================================================================

class Cotizacion(Base, AuditMixin, SoftDeleteMixin):
    """
    Cotización
    Puede convertirse a factura después.
    """
    __tablename__ = "cotizaciones"
    __table_args__ = (
        UniqueConstraint("numero_cotizacion", name="uq_cotizaciones_numero"),
        Index("idx_cotizaciones_numero", "numero_cotizacion"),
        Index("idx_cotizaciones_cliente_id", "cliente_id"),
        Index("idx_cotizaciones_estado", "estado"),
        Index("idx_cotizaciones_fecha_creacion", "created_at"),
    )

    id = Column(Integer, primary_key=True)
    
    # ===== IDENTIFICACIÓN =====
    numero_cotizacion = Column(String(50), unique=True, nullable=False)  # COT-2025-001
    
    # ===== REFERENCIAS (CROSS-SCHEMA FK) =====
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("public.usuarios.id"), nullable=False)  # ← Cross-schema
    
    # ===== CONTENIDO =====
    subtotal = Column(Numeric(12, 4), nullable=False)
    descuento_total = Column(Numeric(12, 4), default=0)
    igv_total = Column(Numeric(12, 4), default=0)
    total = Column(Numeric(12, 4), nullable=False)
    
    # ===== MONEDA =====
    moneda = Column(String(3), default="PEN")
    
    # ===== ESTADO =====
    estado = Column(String(50), default="borrador")  # borrador | enviada | aceptada | rechazada | vencida | convertida
    
    # ===== VALIDEZ =====
    vigencia_dias = Column(Integer, default=30)
    fecha_vencimiento = Column(Date)
    
    # ===== CONVERSIÓN A FACTURA =====
    convertida_a_factura_id = Column(Integer, ForeignKey("facturas.id"))
    
    # ===== NOTAS =====
    notas_internas = Column(String(1000))
    terminos_condiciones = Column(String(2000))
    
    # ===== SOFT DELETE =====
    deleted_at = Column(DateTime)
    
    # ===== RELACIONES =====
    cliente = relationship("Cliente", back_populates="cotizaciones")
    items = relationship("ItemCotizacion", back_populates="cotizacion", cascade="all, delete-orphan")
    factura = relationship("Factura", back_populates="cotizacion")
    
    def __repr__(self):
        return f"<Cotizacion(numero={self.numero_cotizacion}, cliente_id={self.cliente_id})>"


# ============================================================================
# TABLA: ITEMS_COTIZACION
# ============================================================================

class ItemCotizacion(Base):
    """
    Línea de un item en una cotización.
    """
    __tablename__ = "items_cotizacion"
    __table_args__ = (
        UniqueConstraint("cotizacion_id", "producto_id", name="uq_items_cot_producto"),
        Index("idx_items_cot_cotizacion_id", "cotizacion_id"),
    )

    id = Column(Integer, primary_key=True)
    
    # ===== REFERENCIAS =====
    cotizacion_id = Column(Integer, ForeignKey("cotizaciones.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    
    # ===== CANTIDAD Y PRECIO =====
    cantidad = Column(Numeric(12, 4), nullable=False)
    precio_unitario = Column(Numeric(12, 4), nullable=False)
    
    # ===== IMPUESTO =====
    igv_porcentaje = Column(Integer, default=1800)  # 18.00%
    igv_monto = Column(Numeric(12, 4))
    
    # ===== TOTALES =====
    subtotal = Column(Numeric(12, 4), nullable=False)
    total = Column(Numeric(12, 4), nullable=False)
    
    # ===== ORDEN =====
    orden_item = Column(Integer)
    
    # ===== METADATA =====
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # ===== RELACIONES =====
    cotizacion = relationship("Cotizacion", back_populates="items")
    producto = relationship("Producto", back_populates="items_cotizacion")
    
    def __repr__(self):
        return f"<ItemCotizacion(cotizacion_id={self.cotizacion_id}, producto_id={self.producto_id})>"


# ============================================================================
# TABLA: FACTURAS (SUNAT READY)
# ============================================================================

class Factura(Base, AuditMixin, SoftDeleteMixin):
    """
    Factura electrónica enviada a SUNAT.
    """
    __tablename__ = "facturas"
    __table_args__ = (
        UniqueConstraint("numero_serie", "numero_comprobante", name="uq_facturas_numero_sunat"),
        Index("idx_facturas_numero_serie", "numero_serie"),
        Index("idx_facturas_numero_comprobante", "numero_comprobante"),
        Index("idx_facturas_cliente_id", "cliente_id"),
        Index("idx_facturas_estado", "estado"),
        Index("idx_facturas_estado_sunat", "estado_sunat"),
        Index("idx_facturas_fecha_emision", "fecha_emision"),
        Index("idx_facturas_created_at", "created_at"),
    )

    id = Column(Integer, primary_key=True)
    
    # ===== SUNAT IDENTIFICACIÓN =====
    numero_serie = Column(String(4), nullable=False)        # F001, B001, etc
    numero_comprobante = Column(String(8), nullable=False)  # 000001-999999
    
    # ===== REFERENCIAS (CROSS-SCHEMA FK) =====
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("public.usuarios.id"), nullable=False)  # ← Cross-schema
    cotizacion_id = Column(Integer, ForeignKey("cotizaciones.id"))  # Opcional
    
    # ===== TIPO DE COMPROBANTE (SUNAT) =====
    tipo_comprobante = Column(String(2), default="01")  # 01=Factura, 03=Boleta, 07=NC, 08=ND
    
    # ===== TIPO DE OPERACIÓN (SUNAT - CRÍTICO) =====
    # 0101: Venta Interna
    # 0200: Exportación
    # 1001: Venta Sujeta a Confirmación del Comprador
    # etc
    tipo_operacion = Column(String(4), default="0101")
    
    # ===== MONEDA =====
    moneda = Column(String(3), default="PEN")
    
    # ===== DATOS FISCALES =====
    subtotal = Column(Numeric(12, 4), nullable=False)
    descuento_total = Column(Numeric(12, 4), default=0)
    igv_total = Column(Numeric(12, 4), nullable=False)
    total = Column(Numeric(12, 4), nullable=False)
    
    # ===== FECHAS Y HORAS (SUNAT REQUIERE HORA) =====
    fecha_emision = Column(Date, nullable=False)
    hora_emision = Column(Time, nullable=False)  # ← NUEVO: SUNAT requiere hora exacta en XML
    fecha_vencimiento = Column(Date)
    
    # ===== FORMA DE PAGO (SUNAT - CRÍTICO) =====
    # "Contado", "Crédito"
    forma_pago = Column(String(50), default="Contado")
    
    # ===== DETALLE DE CRÉDITO (SI FORMA_PAGO = CRÉDITO) =====
    # JSON: [
    #   {"cuota": 1, "monto": 500, "fecha_pago": "2025-02-28"},
    #   {"cuota": 2, "monto": 500, "fecha_pago": "2025-03-31"}
    # ]
    detalle_credito = Column(JSON)  # Array de cuotas
    
    # ===== UBIGEOS (SUNAT) =====
    ubigeo_origen = Column(String(6))  # UBIGEO de donde sale el producto
    ubigeo_destino = Column(String(6))  # UBIGEO del cliente
    
    # ===== ESTADO =====
    estado = Column(String(50), default="borrador")  # borrador | pendiente_firma | firmada | pendiente_sunat | aceptada | rechazada
    
    # ===== XML Y FIRMA DIGITAL =====
    xml_generado = Column(String)  # XML sin firmar
    xml_firmado = Column(LargeBinary)  # XML firmado (binario)
    
    # ===== CÓDIGO HASH (SUNAT - SE IMPRIME EN PDF) =====
    # El digest value del XML firmado
    codigo_hash = Column(String(100))  # SHA1 del XML firmado
    
    # ===== RESPUESTA DE SUNAT =====
    numero_cdr = Column(String(50))  # Comprobante de Recepción de SUNAT
    estado_sunat = Column(String(50))  # Aceptado | Rechazado
    respuesta_sunat = Column(JSON)  # Respuesta completa de SUNAT en JSON
    
    # ===== REINTENTOS (PARA ENVÍO A SUNAT) =====
    intentos_sunat = Column(Integer, default=0)
    ultimo_intento_sunat = Column(DateTime)
    proximo_intento_sunat = Column(DateTime)
    
    # ===== PDF =====
    pdf_url = Column(String(500))  # URL del PDF generado
    
    # ===== SOFT DELETE =====
    deleted_at = Column(DateTime)
    
    # ===== RELACIONES =====
    cliente = relationship("Cliente", back_populates="facturas")
    items = relationship("ItemFactura", back_populates="factura", cascade="all, delete-orphan")
    cotizacion = relationship("Cotizacion", back_populates="factura")
    
    def __repr__(self):
        return f"<Factura(numero={self.numero_serie}-{self.numero_comprobante}, cliente_id={self.cliente_id})>"


# ============================================================================
# TABLA: ITEMS_FACTURA (CON CAMPOS SUNAT)
# ============================================================================

class ItemFactura(Base):
    """
    Línea de un item en una factura.
    Incluye campos específicos para SUNAT.
    """
    __tablename__ = "items_factura"
    __table_args__ = (
        UniqueConstraint("factura_id", "producto_id", name="uq_items_fact_producto"),
        Index("idx_items_fact_factura_id", "factura_id"),
    )

    id = Column(Integer, primary_key=True)
    
    # ===== REFERENCIAS =====
    factura_id = Column(Integer, ForeignKey("facturas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    
    # ===== CANTIDAD Y PRECIO =====
    cantidad = Column(Numeric(12, 4), nullable=False)
    precio_unitario = Column(Numeric(12, 4), nullable=False)
    
    # ===== TIPO DE AFECTACIÓN IGV (SUNAT - CRÍTICO) =====
    # 10: Gravado - Operación Onerosa (18%)
    # 20: Exonerado
    # 30: Inafecto
    # 40: Exportación
    tipo_afectacion_igv = Column(String(2), default="10")
    
    # ===== IMPUESTO =====
    igv_porcentaje = Column(Integer, default=1800)
    igv_monto = Column(Numeric(12, 4))
    
    # ===== CÓDIGO PRODUCTO SUNAT (OPCIONAL PERO RECOMENDADO) =====
    # UNSPSC code
    codigo_producto_sunat = Column(String(8))
    
    # ===== TOTALES =====
    subtotal = Column(Numeric(12, 4), nullable=False)
    total = Column(Numeric(12, 4), nullable=False)
    
    # ===== ORDEN =====
    orden_item = Column(Integer)
    
    # ===== METADATA =====
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # ===== RELACIONES =====
    factura = relationship("Factura", back_populates="items")
    producto = relationship("Producto", back_populates="items_factura")
    
    def __repr__(self):
        return f"<ItemFactura(factura_id={self.factura_id}, producto_id={self.producto_id})>"


# ============================================================================
# TABLA: SECUENCIAS (CRÍTICA PARA NUMERACIÓN SUNAT)
# ============================================================================

class Secuencia(Base):
    """
    Maneja la numeración secuencial de comprobantes para SUNAT.
    
    SUNAT exige que la numeración sea CONSECUTIVA sin saltos.
    Cada serie (F001, F002, B001, etc) tiene su propio contador.
    """
    __tablename__ = "secuencias"
    __table_args__ = (
        UniqueConstraint("tipo_documento", "serie", name="uq_secuencias_tipo_serie"),
        Index("idx_secuencias_tipo_documento", "tipo_documento"),
        Index("idx_secuencias_serie", "serie"),
    )

    id = Column(Integer, primary_key=True)
    
    # ===== TIPO DE DOCUMENTO SUNAT =====
    tipo_documento = Column(String(2), nullable=False)  # 01=Factura, 03=Boleta, 07=NC, 08=ND
    
    # ===== SERIE =====
    serie = Column(String(4), nullable=False)  # F001, F002, B001, B002, etc
    
    # ===== PRÓXIMO NÚMERO A USAR =====
    proximo_numero = Column(Integer, default=1)  # 1-999999
    
    # ===== METADATA =====
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Secuencia(tipo={self.tipo_documento}, serie={self.serie}, proximo={self.proximo_numero})>"


# ============================================================================
# TABLA: NOTAS DE COMPROBANTE (Crédito/Débito - SUNAT READY)
# ============================================================================

class NotaComprobante(Base, AuditMixin):
    """
    Nota de Crédito (devolución) o Débito (ajuste).
    Se emite contra una factura existente.
    También se envía a SUNAT.
    """
    __tablename__ = "notas_comprobante"
    __table_args__ = (
        UniqueConstraint("tipo", "numero_serie", "numero_comprobante", name="uq_notas_numero"),
        Index("idx_notas_tipo", "tipo"),
        Index("idx_notas_factura_id", "factura_referenciada_id"),
    )

    id = Column(Integer, primary_key=True)
    
    # ===== TIPO DE NOTA =====
    tipo = Column(String(20), nullable=False)  # credito | debito
    
    # ===== SUNAT NUMERACIÓN =====
    numero_serie = Column(String(4), nullable=False)  # NC01, ND01, etc
    numero_comprobante = Column(String(8), nullable=False)
    
    # ===== TIPO DE OPERACIÓN (SUNAT) =====
    # 0101: Devolución por compra de biens
    # 0200: Devolución por servicios
    # etc
    tipo_operacion = Column(String(4), default="0101")
    
    # ===== REFERENCIA =====
    factura_referenciada_id = Column(Integer, ForeignKey("facturas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("public.usuarios.id"), nullable=False)  # ← Cross-schema
    
    # ===== RAZÓN (CÓDIGO SUNAT) =====
    # 01: Devolución total
    # 02: Devolución parcial
    # 03: Descuento
    # 04: Ajuste por error
    motivo = Column(String(2), nullable=False)
    descripcion = Column(String(500))
    
    # ===== MONTO =====
    monto = Column(Numeric(12, 4), nullable=False)
    
    # ===== ESTADOS =====
    estado = Column(String(50), default="borrador")
    
    # ===== XML Y SUNAT =====
    xml_generado = Column(String)
    xml_firmado = Column(LargeBinary)
    codigo_hash = Column(String(100))  # Hash del XML
    numero_cdr = Column(String(50))
    estado_sunat = Column(String(50))
    respuesta_sunat = Column(JSON)
    
    # ===== REINTENTOS =====
    intentos_sunat = Column(Integer, default=0)
    ultimo_intento_sunat = Column(DateTime)
    proximo_intento_sunat = Column(DateTime)
    
    # ===== METADATA =====
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ===== RELACIONES =====
    factura = relationship("Factura")
    
    def __repr__(self):
        return f"<NotaComprobante(tipo={self.tipo}, numero={self.numero_serie}-{self.numero_comprobante})>"


# ============================================================================
# TABLA: AUDIT_LOGS (Auditoría por tenant)
# ============================================================================

class AuditLog(Base):
    """
    Log de auditoría específico del tenant.
    Registra todas las acciones en datos de esta empresa.
    """
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_logs_usuario_id", "usuario_id"),
        Index("idx_audit_logs_timestamp", "created_at"),
        Index("idx_audit_logs_accion", "accion"),
    )

    id = Column(Integer, primary_key=True)
    
    # ===== QUIÉN =====
    usuario_id = Column(Integer, ForeignKey("public.usuarios.id"), nullable=False)  # ← Cross-schema
    
    # ===== QUÉ =====
    accion = Column(String(100), nullable=False)  # crear_factura, actualizar_cliente, etc
    tabla = Column(String(100), nullable=False)
    registro_id = Column(Integer)
    
    # ===== CAMBIOS =====
    cambios = Column(String(2000))  # JSON: {"campo": ["viejo", "nuevo"]}
    descripcion = Column(String(500))
    
    # ===== RED =====
    ip_usuario = Column(String(45))
    user_agent = Column(String(500))
    
    # ===== TIMESTAMP =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<AuditLog(accion={self.accion}, tabla={self.tabla})>"