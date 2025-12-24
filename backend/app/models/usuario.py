from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Usuario(Base):
    __tablename__ = "Usuarios"

    id_usuario = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, ForeignKey("Empresas.id_empresa"), nullable=False)
    empresa = relationship("Empresa")
    email = Column(String(255), nullable=False, unique=True)
    clave_hash = Column(String(255), nullable=False)
    nombres = Column(String(255), nullable=False)
    esta_activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_cierre = Column(DateTime, nullable=True)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  