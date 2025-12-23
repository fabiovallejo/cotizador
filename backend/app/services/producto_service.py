from app.models.producto import Producto
from app.core.tenant import get_current_company_id
from sqlalchemy.exc import IntegrityError

def listar_productos(db):
    company_id = get_current_company_id()
    productos = (
        db.query(Producto)
        .filter(Producto.id_empresa == company_id, Producto.esta_activo == True)
        .all()
    )
    return productos

def crear_producto(db, payload):
    company_id = get_current_company_id()

    if payload.get("precio", 0) <= 0:
        return None

    producto = Producto(
        id_empresa=company_id,
        SKU=payload["SKU"].strip(),
        nombre=payload["nombre"].strip(),
        precio=payload["precio"],
        descripcion=payload.get("descripcion")
    )

    db.add(producto)
    try:
        db.commit()
        db.refresh(producto)
        return producto
    except IntegrityError:
        db.rollback()
        return None