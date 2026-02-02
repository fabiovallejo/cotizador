from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class createUsuarioRequest(BaseModel):
    email: EmailStr
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: Optional[str] = None
    password: str = Field(..., min_length=8, max_length=72)
    rol: str = Field(..., pattern="^(administrador|contador|gerente_ventas|vendedor|operario|readonly)$")

class updateUsuarioRequest(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    rol: Optional[str] = Field(None, pattern="^(administrador|contador|gerente_ventas|vendedor|operario|readonly)$")
    estado: Optional[str] = Field(None, pattern="^(activo|inactivo|bloqueado)$")
    
class usuarioResponse(BaseModel):
    id: int
    empresa_id: int
    email: str
    nombre: str
    apellido: Optional[str] = None
    rol: str
    estado: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True