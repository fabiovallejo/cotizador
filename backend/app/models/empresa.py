from sqlalchemy import Column, Integer, String, Boolean, DateTime, CHAR
from datetime import datetime
from app.core.database import Base

class Empresa(Base):
    __tablename__ = "Empresas"

    id_empresa = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    razon_social = Column(String(255), nullable=False)
    ruc = Column(CHAR(11), nullable=False, unique=True)
    esta_activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)