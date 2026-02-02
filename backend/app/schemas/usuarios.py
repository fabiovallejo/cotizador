from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
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


# ============================================================================
# CAMBIAR CONTRASEÑA
# ============================================================================

class CambiarPasswordRequest(BaseModel):
    password_actual: str = Field(..., min_length=8)
    password_nuevo: str = Field(..., min_length=8, max_length=72)
    
    @field_validator('password_nuevo')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError('Debe contener al menos una mayúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('Debe contener al menos un número')
        return v
    
    @model_validator(mode='after')
    def password_diferente(self):
        if self.password_actual == self.password_nuevo:
            raise ValueError('La nueva contraseña debe ser diferente a la actual')
        return self


class CambiarPasswordResponse(BaseModel):
    mensaje: str = "Contraseña actualizada correctamente"


# ============================================================================
# MI PERFIL
# ============================================================================

class UpdateMiPerfilRequest(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(None, max_length=100)


class MiPerfilResponse(BaseModel):
    id: int
    email: str
    nombre: str
    apellido: Optional[str] = None
    rol: str
    estado: str
    empresa_id: int
    created_at: datetime
    ultimo_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# RECUPERAR CONTRASEÑA
# ============================================================================

class OlvidePasswordRequest(BaseModel):
    email: EmailStr


class OlvidePasswordResponse(BaseModel):
    mensaje: str = "Si el email existe, recibirá instrucciones"
    # Solo en desarrollo:
    token: Optional[str] = None


class ResetearPasswordRequest(BaseModel):
    password_nuevo: str = Field(..., min_length=8, max_length=72)
    
    @field_validator('password_nuevo')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError('Debe contener al menos una mayúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('Debe contener al menos un número')
        return v


class ResetearPasswordResponse(BaseModel):
    mensaje: str = "Contraseña restablecida correctamente"