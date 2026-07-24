from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# ============================================================================
# CREAR CUENTA BANCARIA
# ============================================================================

class CuentaBancariaCreate(BaseModel):
    nombre_banco: str = Field(..., min_length=2, max_length=100)
    numero_cuenta: str = Field(..., min_length=5, max_length=50)
    cci: Optional[str] = Field(None, max_length=25)
    moneda: str = Field(..., pattern="^(PEN|USD)$")
    tipo_cuenta: str = Field(..., pattern="^(corriente|ahorros)$")
    titular: str = Field(..., min_length=2, max_length=255)


# ============================================================================
# ACTUALIZAR CUENTA BANCARIA
# ============================================================================

class CuentaBancariaUpdate(BaseModel):
    nombre_banco: Optional[str] = Field(None, min_length=2, max_length=100)
    numero_cuenta: Optional[str] = Field(None, min_length=5, max_length=50)
    cci: Optional[str] = Field(None, max_length=25)
    moneda: Optional[str] = Field(None, pattern="^(PEN|USD)$")
    tipo_cuenta: Optional[str] = Field(None, pattern="^(corriente|ahorros)$")
    titular: Optional[str] = Field(None, min_length=2, max_length=255)
    activo: Optional[bool] = None


# ============================================================================
# RESPONSE
# ============================================================================

class CuentaBancariaResponse(BaseModel):
    id: int
    empresa_id: int
    nombre_banco: str
    numero_cuenta: str
    cci: Optional[str] = None
    moneda: str
    tipo_cuenta: str
    titular: str
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
