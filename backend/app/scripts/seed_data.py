from app.core.database import SessionLocal
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.usuario_rol import UsuarioRol
from app.core.security import hash_password

def seed():
    db = SessionLocal()

    # 1. Crear empresa
    empresa = Empresa(
        nombre="Empresa Demo",
        razon_social="Empresa Demo SAC",
        ruc="20123456789"
    )
    db.add(empresa)
    db.commit()
    db.refresh(empresa)

    # 2. Crear rol Owner
    rol_owner = Rol(
        id_empresa=empresa.id_empresa,
        nombre="Owner",
        descripcion="Administrador de la empresa"
    )
    db.add(rol_owner)
    db.commit()
    db.refresh(rol_owner)

    # 3. Crear usuario admin
    usuario = Usuario(
        id_empresa=empresa.id_empresa,
        email="admin@empresa.com",
        clave_hash=hash_password("12345678"),
        nombres="Administrador"
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    # 4. Asignar rol al usuario
    usuario_rol = UsuarioRol(
        id_usuario=usuario.id_usuario,
        id_rol=rol_owner.id_rol
    )
    db.add(usuario_rol)
    db.commit()

    db.close()

    print("Datos semilla creados correctamente")

if __name__ == "__main__":
    seed()
