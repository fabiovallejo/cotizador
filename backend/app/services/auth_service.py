from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.core.security import verify_password

def authenticate_user(db: Session, email: str, password: str):

    # 1. Buscar usuario activo por email
    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.email == email,
            Usuario.esta_activo == True
        )
        .first()
    )

    if not usuario:
        return None

    # 2. Verificar password
    if not verify_password(password, usuario.clave_hash):
        return None

    # 3. Obtener roles del usuario
    roles_usuario = (
        db.query(UsuarioRol)
        .filter(UsuarioRol.id_usuario == usuario.id_usuario)
        .all()
    )

    roles = [ur.rol.nombre for ur in roles_usuario]

    # 4. Retornar datos mínimos para JWT
    return {
        "id_usuario": usuario.id_usuario,
        "id_empresa": usuario.id_empresa,
        "roles": roles
    }
