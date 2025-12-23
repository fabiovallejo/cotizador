from app.models.cliente import Cliente
from app.core.tenant import get_current_company_id
from sqlalchemy.exc import IntegrityError

def listar_clientes(db):
    company_id = get_current_company_id()
    clientes = (
        db.query(Cliente)
        .filter(Cliente.id_empresa == company_id, Cliente.esta_activo == True)
        .all()
    )
    return clientes

def crear_cliente(db, payload):
    company_id = get_current_company_id()

    cliente = Cliente(
        id_empresa=company_id,
        numero_documento=payload["numero_documento"].strip(),
        nombre_o_razon_social=payload["nombre_o_razon_social"].strip(),
    )

    db.add(cliente)
    try:
        db.commit()
        db.refresh(cliente)
        return cliente
    except IntegrityError:
        db.rollback()
        return None