from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Cliente(Base):
    __tablename__ = "Clientes"

    __table_args__ = (
        UniqueConstraint("id_empresa", "numero_documento", name="uq_cliente_empresa_documento"),
    )

    id_cliente = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("Empresas.id_empresa"), nullable=False)
    empresa = relationship("Empresa")
    numero_documento = Column(String(11), nullable=False)
    nombre_o_razon_social = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    telefono = Column(String(15), nullable=True)
    direccion = Column(String(255), nullable=True)
    esta_activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)