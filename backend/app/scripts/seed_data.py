from app.core.database import SessionLocal
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.rol import Rol
from app.models.usuario_rol import UsuarioRol
from app.core.security import hash_password

def seed():
    db = SessionLocal()

    empresa = db.query(Empresa).filter_by(ruc="20123456789").first()

    if not empresa:
        empresa = Empresa(
            nombre="Empresa Demo",
            razon_social="Empresa Demo SAC",
            ruc="20123456789"
        )
        db.add(empresa)
        db.commit()
        db.refresh(empresa)

    rol_owner = db.query(Rol).filter_by(
        id_empresa=empresa.id_empresa,
        nombre="Owner"
    ).first()

    if not rol_owner:
        rol_owner = Rol(
            id_empresa=empresa.id_empresa,
            nombre="Owner",
            descripcion="Administrador de la empresa"
        )
        db.add(rol_owner)
        db.commit()
        db.refresh(rol_owner)

    usuario = db.query(Usuario).filter_by(
        email="admin@empresa.com"
    ).first()

    if not usuario:
        usuario = Usuario(
            id_empresa=empresa.id_empresa,
            email="admin@empresa.com",
            clave_hash=hash_password("12345678"),
            nombres="Administrador"
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

    existe_rol = db.query(UsuarioRol).filter_by(
        id_usuario=usuario.id_usuario,
        id_rol=rol_owner.id_rol
    ).first()

    if not existe_rol:
        usuario_rol = UsuarioRol(
            id_usuario=usuario.id_usuario,
            id_rol=rol_owner.id_rol
        )
        db.add(usuario_rol)
        db.commit()

    cliente = db.query(Cliente).filter_by(
        id_empresa=empresa.id_empresa,
        numero_documento="12345678"
    ).first()

    if not cliente:
        cliente = Cliente(
            id_empresa=empresa.id_empresa,
            numero_documento="12345678",
            nombre_o_razon_social="Cliente Demo SAC",
            email="cliente@demo.com"
        )
        db.add(cliente)
        db.commit()

    db.close()

    print("Datos semilla creados correctamente")

if __name__ == "__main__":
    seed()
