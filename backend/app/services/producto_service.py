from app.models.producto import Producto
from app.core.tenant import get_current_company_id
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import or_

def listar_productos(db: Session, id_empresa: int, search: str | None = None):
    query = (
        db.query(Producto)
        .filter(
            Producto.id_empresa == id_empresa,
            Producto.esta_activo == True
        )
    )

    if search:
        query = query.filter(
            or_(
                Producto.nombre.ilike(f"%{search}%"),
                Producto.SKU.ilike(f"%{search}%")
            )
        )

    return query.order_by(Producto.nombre.asc()).all()

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