from flask_jwt_extended import get_jwt

def get_current_company_id():
    return get_jwt()["id_empresa"]
