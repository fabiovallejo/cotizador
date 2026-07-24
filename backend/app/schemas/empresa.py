from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConfiguracionEmpresaResponse(BaseModel):
    id: int
    empresa_id: int
    
    # Series de comprobantes
    serie_factura: Optional[str] = "F001"
    serie_boleta: Optional[str] = "B001"
    serie_nc: Optional[str] = "NC01"
    serie_nd: Optional[str] = "ND01"
    
    # Certificado digital
    ruta_certificado: Optional[str] = None
    # No exponemos contraseña_certificado por seguridad
    
    # Datos para PDF
    logo_url: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UpdateConfiguracionEmpresaRequest(BaseModel):
    # Series de comprobantes
    serie_factura: Optional[str] = None
    serie_boleta: Optional[str] = None
    serie_nc: Optional[str] = None
    serie_nd: Optional[str] = None
    
    # Certificado digital
    ruta_certificado: Optional[str] = None
    contraseña_certificado: Optional[str] = None
    
    # Datos para PDF
    logo_url: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
