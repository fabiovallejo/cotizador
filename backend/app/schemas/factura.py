# app/schemas/factura.py

from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class CreateItemFacturaRequest(BaseModel):
    producto_id: int
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., gt=0)
    igv_porcentaje: int = Field(default=18, ge=0, le=100)

class CreateFacturaRequest(BaseModel):
    cliente_id: int
    moneda: str = Field(default="PEN", pattern="^(PEN|USD)$")
    tipo_cambio: Optional[Decimal] = Field(None, gt=0)
    numero_serie: Optional[str] = None
    tipo_operacion: Optional[str] = None
    forma_pago: Optional[str] = None
    items: List[CreateItemFacturaRequest]

class FacturaResponse(BaseModel):
    id: int
    numero_serie: str
    numero_comprobante: str
    cliente_id: int
    moneda: str
    tipo_cambio: Optional[Decimal] = None
    subtotal: Decimal
    igv_total: Decimal
    total: Decimal
    subtotal_en_pen: Optional[Decimal] = None
    total_en_pen: Optional[Decimal] = None
    estado: str
    
    class Config:
        from_attributes = True


class ItemFacturaResponse(BaseModel):
    id: int
    factura_id: int
    producto_id: int
    cantidad: Decimal
    precio_unitario: Decimal
    moneda_original: Optional[str] = None
    precio_original: Optional[Decimal] = None
    tipo_cambio_usado: Optional[Decimal] = None
    precio_en_factura: Decimal
    igv_porcentaje: Decimal
    igv_monto: Decimal
    subtotal: Decimal
    total: Decimal
    tipo_afectacion_igv: str = "10"
    orden_item: Optional[int] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True