from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class ClienteResponse(BaseModel):
    """
    Schema para RESPONDER al frontend.
    """
    id: int
    tipo_documento: str
    numero_documento: str
    razon_social: str
    nombre_comercial: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion_completa: Optional[str] = None
    ubigeo: Optional[str] = None
    es_cliente_frecuente: bool = False
    estado: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ClienteRequest(BaseModel):
    """
    Schema para CREAR o ACTUALIZAR un cliente.
    Validamos los datos antes de que toquen la BD.
    """
    tipo_documento: str = Field(..., max_length=10, description="Tipo de documento (RUC, DNI, Pasaporte, Otros)")
    numero_documento: str = Field(..., max_length=20, min_length=8)
    razon_social: str = Field(..., min_length=3, max_length=255)
    nombre_comercial: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, min_length=7, max_length=15)
    direccion_completa: Optional[str] = Field(None, max_length=500)
    ubigeo: Optional[str] = Field(None, pattern=r"^\d{6}$", description="Código de 6 dígitos de Ubicación Geográfica")
    es_cliente_frecuente: bool = False
    estado: str = "activo"
