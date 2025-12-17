import os
from passlib.context import CryptContext

BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

def _apply_pepper(password: str) -> str:
    pepper = os.getenv("PASSWORD_PEPPER", "")
    return password + pepper

def hash_password(password: str) -> str:
    if not password or len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")
    return pwd_context.hash(_apply_pepper(password), rounds=BCRYPT_ROUNDS)

def verify_password(password: str, password_hash: str) -> bool:
    if not password or not password_hash:
        return False
    return pwd_context.verify(_apply_pepper(password), password_hash)
