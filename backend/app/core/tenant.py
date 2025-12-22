from flask_jwt_extended import get_jwt_identity

def get_current_company_id():
    identity = get_jwt_identity()
    return identity.get("id_empresa")
