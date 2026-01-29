from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductoResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    codigo_unspsc: Optional[str] = None
    tipo: str
    categoria: Optional[str] = None
    marca: Optional[str] = None
    precio_unitario: Decimal
    costo_unitario: Optional[Decimal] = None
    precio_distribuidor: Optional[Decimal] = None
    aplica_igv: bool
    igv_porcentaje: int
    tipo_afectacion_igv: str
    moneda: str
    unidad_medida: str
    tiene_stock: bool
    cantidad_stock: int
    estado: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProductoRequest(BaseModel):
    codigo: str = Field(..., max_length=100, min_length=1, description="SKU o código del producto")
    nombre: str = Field(..., max_length=255, min_length=3, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, max_length=1000)
    codigo_unspsc: Optional[str] = Field(None, pattern=r"^\d{8}$", description="Código de 8 dígitos UNSPSC")
    tipo: str = Field(default="producto", max_length=50, description="producto | servicio | combo")
    categoria: Optional[str] = Field(None, max_length=100)
    marca: Optional[str] = Field(None, max_length=100)
    precio_unitario: Decimal = Field(..., gt=0, description="Precio de venta unitario")
    costo_unitario: Optional[Decimal] = Field(None, ge=0)
    precio_distribuidor: Optional[Decimal] = Field(None, ge=0)
    aplica_igv: bool = Field(default=True, description="Si aplica IGV")
    igv_porcentaje: int = Field(default=1800, description="Porcentaje IGV en centésimas (1800 = 18%)")
    tipo_afectacion_igv: str = Field(default="10", pattern=r"^\d{2}$", description="10=Gravado, 20=Exonerado, 30=Inafecto")
    moneda: str = Field(default="PEN", max_length=3, description="PEN, USD, EUR")
    unidad_medida: str = Field(default="UND", max_length=20, description="UND, KG, LTR, etc")
    tiene_stock: bool = Field(default=False, description="Si maneja inventario")
    cantidad_stock: int = Field(default=0, ge=0, description="Cantidad en stock")
    estado: str = Field(default="activo", description="activo | inactivo")