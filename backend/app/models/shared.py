"""
Modelos del Schema PUBLIC (compartido entre todos los tenants).

Estos modelos están en schema="public" y NO tienen isolamiento por tenant.
Son datos "globales" del sistema SaaS.
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, 
    ForeignKey, Index, UniqueConstraint, JSON, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.base import Base, TimestampMixin, SoftDeleteMixin, AuditMixin

# ============================================================================
# TABLA: EMPRESAS (Metadata de clientes del SaaS)
# ============================================================================

class Empresa(Base, AuditMixin, SoftDeleteMixin):
    """
    Representa una empresa (cliente) del SaaS.
    
    Cada empresa:
    - Tiene un schema asignado en PostgreSQL (ej: empresa_1, empresa_abc)
    - Sus propios datos aislados en ese schema
    - Certificado digital para SUNAT
    - Información SUNAT para emisión de comprobantes
    """
    __tablename__ = "empresas"
    __table_args__ = (
        Index("idx_empresas_ruc", "ruc"),
        Index("idx_empresas_db_schema", "db_schema"),
        Index("idx_empresas_estado", "estado"),
        {"schema": "public"},
    )

    id = Column(Integer, primary_key=True)
    
    # ===== IDENTIFICACIÓN FISCAL =====
    ruc = Column(String(11), unique=True, nullable=False)
    razon_social = Column(String(255), nullable=False)
    nombre_comercial = Column(String(255))
    
    # ===== SCHEMA EN POSTGRESQL =====
    db_schema = Column(String(50), unique=True, nullable=False)
    
    # ===== INFORMACIÓN DE CONTACTO =====
    email = Column(String(255))
    telefono = Column(String(20))
    direccion = Column(String(500))
    
    # ===== UBIGEO (Código de ubicación geográfica) =====
    ubigeo = Column(String(6)) 
    
    # ===== CERTIFICADO DIGITAL (Para firma de XML) =====
    certificado_digital_path = Column(String(500))
    certificado_password_hash = Column(String(255))
    certificado_expiracion = Column(DateTime)
    
    # ===== CONFIGURACIÓN SUNAT =====
    ambiente_sunat = Column(String(20), default="beta")  # beta | produccion
    usuario_sol = Column(String(50))
    
    # ===== DATOS FISCALES =====
    moneda_base = Column(String(3), default="PEN")
    aplicar_igv_defecto = Column(Boolean, default=True)
    igv_porcentaje = Column(Numeric(10, 2), default=18.00)
    
    # ===== DOMICILIO FISCAL =====
    direccion_fiscal = Column(String(500)) 
    ubigeo_fiscal = Column(String(6)) 
    
    # ===== INFORMACIÓN DE ESTABLECIMIENTO =====
    numero_establecimiento = Column(Integer, default=0)  # 0 = Matriz, 1+ = Sucursales
    
    # ===== PLAN/SUSCRIPCIÓN =====
    plan_id = Column(Integer)
    
    # ===== ESTADO =====
    estado = Column(String(20), default="activa")  # activa | suspendida | eliminada
    deleted_at = Column(DateTime)
    
    # ===== METADATA =====
    logo_url = Column(String(500))
    
    # ===== RELACIONES =====
    usuarios = relationship("Usuario", back_populates="empresa", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Empresa(ruc={self.ruc}, schema={self.db_schema})>"


# ============================================================================
# TABLA: USUARIOS (Usuarios del SaaS - schema público)
# ============================================================================

class Usuario(Base, AuditMixin, SoftDeleteMixin):
    """
    Usuario del SaaS (administrador, contador, vendedor).
    
    Está en schema público pero aislado por empresa_id en JWT.
    """
    __tablename__ = "usuarios"
    __table_args__ = (
        Index("idx_usuarios_email", "email"),
        Index("idx_usuarios_empresa_id", "empresa_id"),
        Index("idx_usuarios_estado", "estado"),
        UniqueConstraint("email", name="uq_usuarios_email"),
        {"schema": "public"},
    )

    id = Column(Integer, primary_key=True)
    
    # ===== EMPRESA A LA QUE PERTENECE =====
    empresa_id = Column(Integer, ForeignKey("public.empresas.id"), nullable=False, index=True)
    
    # ===== CREDENCIALES =====
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # ===== INFORMACIÓN PERSONAL =====
    nombre = Column(String(255), nullable=False)
    apellido = Column(String(255))
    
    # ===== ROL (PERMISOS) =====
    rol = Column(String(50), default="vendedor")  # admin | contador | vendedor | readonly
    
    # ===== ESTADO =====
    estado = Column(String(20), default="activo")  # activo | inactivo | bloqueado
    deleted_at = Column(DateTime)
    
    # ===== SEGURIDAD 2FA =====
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(32))
    
    # ===== AUDITORÍA =====
    ultimo_login = Column(DateTime)
    ip_ultimo_login = Column(String(45))  # IPv4 o IPv6
    
    # ===== RELACIONES =====
    empresa = relationship("Empresa", back_populates="usuarios")
    
    def __repr__(self):
        return f"<Usuario(email={self.email}, empresa_id={self.empresa_id})>"


# ============================================================================
# TABLA: AUDIT_GLOBAL (Auditoría de todas las acciones)
# ============================================================================

class AuditGlobal(Base):
    """
    Log de auditoría global de TODAS las acciones en el sistema.
    Importante para compliance, debugging y seguridad.
    """
    __tablename__ = "audit_global"
    __table_args__ = (
        Index("idx_audit_global_empresa_timestamp", "empresa_id", "created_at"),
        Index("idx_audit_global_usuario_timestamp", "usuario_id", "created_at"),
        Index("idx_audit_global_accion", "accion"),
        {"schema": "public"},
    )

    id = Column(Integer, primary_key=True)
    
    # ===== QUIÉN HIZO LA ACCIÓN =====
    empresa_id = Column(Integer, ForeignKey("public.empresas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("public.usuarios.id"), nullable=False)
    
    # ===== QUÉ HIZO =====
    accion = Column(String(100), nullable=False)  # crear_factura, actualizar_cliente, etc
    tabla = Column(String(100), nullable=False)
    registro_id = Column(Integer)
    
    # ===== DETALLES =====
    cambios = Column(String(2000))  # JSON: {"campo": ["viejo", "nuevo"]}
    descripcion = Column(String(500))
    
    # ===== RED =====
    ip_usuario = Column(String(45))
    user_agent = Column(String(500))
    
    # ===== TIMESTAMP =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<AuditGlobal(accion={self.accion}, tabla={self.tabla})>"


# ============================================================================
# TABLA: CONFIGURACION_EMPRESA (Para series y certificados)
# ============================================================================

class ConfiguracionEmpresa(Base):
    """
    Tabla para guardar la configuración de la empresa.
    Datos para PDF, guaardado de series, certificado digital, etc.
    """
    __tablename__ = "configuracion_empresa"
    
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey("public.empresas.id"))
    
    # SERIE ACTUAL DE COMPROBANTES
    serie_factura = Column(String(4), default="F001")  # F001, F002, etc
    serie_boleta = Column(String(4), default="B001")
    serie_nc = Column(String(4), default="NC01")
    serie_nd = Column(String(4), default="ND01")
    
    # CERTIFICADO DIGITAL (para SUNAT)
    ruta_certificado = Column(String(500))  # /path/to/cert.p12
    contraseña_certificado = Column(String(255))  # Encriptado
    
    # LOGO/DATOS PARA PDF
    logo_url = Column(String(500))
    telefono = Column(String(20))
    email = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)