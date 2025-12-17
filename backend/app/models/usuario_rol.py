from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class UsuarioRol(Base):
    __tablename__ = "UsuariosRoles"

    __table_args__ = (
    UniqueConstraint("id_usuario", "id_rol", name="uq_usuario_rol"),
    )

    id_usuariorol = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"), nullable=False)
    usuario = relationship("Usuario")
    id_rol = Column(Integer, ForeignKey("Roles.id_rol"), nullable=False)
    rol = relationship("Rol")