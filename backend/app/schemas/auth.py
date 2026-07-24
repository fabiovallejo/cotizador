from pydantic import BaseModel, EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    """Schema para la solicitud de login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    usuario_id: int
    empresa_id: int
    rol: str
    db_schema: str
    nombre: str
