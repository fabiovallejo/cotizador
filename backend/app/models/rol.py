from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Rol(Base):
    __tablename__ = "Roles"

    id_rol = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("Empresas.id_empresa"), nullable=False)
    empresa = relationship("Empresa")
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String(255), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow) 