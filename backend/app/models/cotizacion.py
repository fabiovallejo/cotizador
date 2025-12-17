from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Cotizacion(Base):
    __tablename__ = "Cotizaciones"

    __table_args__ = (
        UniqueConstraint("id_empresa", "codigo_cotizacion", name="uq_cotizacion_empresa_codigo"),
    )

    id_cotizacion = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("Empresas.id_empresa"), nullable=False)
    empresa = relationship("Empresa")
    id_cliente = Column(Integer, ForeignKey("Clientes.id_cliente"), nullable=False)
    cliente = relationship("Cliente")
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"), nullable=False)
    usuario = relationship("Usuario")
    codigo_cotizacion = Column(String(255), nullable=False)
    estado = Column(String(50), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)
    monto_descuento = Column(Numeric(12, 2), nullable=True)
    porcentaje_descuento = Column(Numeric(12, 2), nullable=True)
    total = Column(Numeric(12, 2), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)