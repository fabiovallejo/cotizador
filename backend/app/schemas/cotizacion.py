from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date


class CreateItemCotizacionRequest(BaseModel):
    producto_id: int
    cantidad: Decimal = Field(..., gt=0)


class CreateCotizacionRequest(BaseModel):
    cliente_id: int
    moneda: str = Field(default="PEN", pattern="^(PEN|USD)$")
    vigencia_dias: int = Field(default=30, ge=1, le=365)
    notas_internas: Optional[str] = None
    terminos_condiciones: Optional[str] = None
    items: List[CreateItemCotizacionRequest]


class CotizacionResponse(BaseModel):
    id: int
    numero_cotizacion: str
    cliente_id: int
    moneda: str
    tipo_cambio: Optional[Decimal] = None
    subtotal: Decimal
    descuento_total: Decimal
    igv_total: Decimal
    total: Decimal
    estado: str
    vigencia_dias: int
    fecha_vencimiento: Optional[date] = None
    notas_internas: Optional[str] = None
    terminos_condiciones: Optional[str] = None
    convertida_a_factura_id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ItemCotizacionResponse(BaseModel):
    id: int
    cotizacion_id: int
    producto_id: int
    cantidad: Decimal
    precio_unitario: Decimal
    igv_porcentaje: Decimal
    igv_monto: Decimal
    subtotal: Decimal
    total: Decimal
    orden_item: Optional[int] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
