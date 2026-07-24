from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator

class CreateTenantRequest(BaseModel):
    """Schema para crear una empresa y su owner."""
    
    # ===== DATOS DE LA EMPRESA =====
    ruc: str = Field(
        ...,
        min_length=11,
        max_length=11,
        pattern=r"^\d{11}$",
        description="RUC de la empresa (11 dígitos)"
    )
    razon_social: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Razón social de la empresa"
    )
    direccion: Optional[str] = Field(
        None,
        max_length=500,
        description="Dirección fiscal"
    )
    
    # ===== DATOS DEL OWNER =====
    owner_email: EmailStr = Field(..., description="Email del administrador")
    owner_nombre: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombre del administrador"
    )
    owner_apellido: Optional[str] = Field(
        None,
        max_length=100,
        description="Apellido del administrador"
    )
    owner_password: str = Field(
        ...,
        min_length=8,
        max_lenght=72,
        description="Contraseña (mínimo 8 caracteres, máximo 72 caracteres)"
    )
    
    @validator('owner_password')
    def validate_password_strength(cls, v):
        """Valida fortaleza de contraseña."""
        if not any(char.isupper() for char in v):
            raise ValueError('Contraseña debe contener mayúscula')
        if not any(char.isdigit() for char in v):
            raise ValueError('Contraseña debe contener número')
        return v


class CreateTenantResponse(BaseModel):
    """Schema de respuesta al crear empresa."""
    empresa_id: int
    owner_id: int
    owner_email: str
    owner_nombre: str
    message: str