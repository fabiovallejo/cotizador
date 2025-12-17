from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Producto(Base):
    __tablename__ = "Productos"

    __table_args__ = (
        UniqueConstraint("id_empresa", "SKU", name="uq_producto_empresa_sku"),
    )

    id_producto = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("Empresas.id_empresa"), nullable=False)
    empresa = relationship("Empresa")
    SKU = Column(String(75), nullable=False)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String(255), nullable=True)
    precio = Column(Numeric(12, 2), nullable=False)
    esta_activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)