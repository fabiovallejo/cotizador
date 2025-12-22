from passlib.context import CryptContext
import hashlib
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PEPPER = os.getenv("PASSWORD_PEPPER", "")

def _prehash(password: str) -> str:
    combined = (password + PEPPER).encode("utf-8")
    return hashlib.sha256(combined).hexdigest()

def hash_password(password: str) -> str:
    return pwd_context.hash(_prehash(password))

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(_prehash(password), password_hash)