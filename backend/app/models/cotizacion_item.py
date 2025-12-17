from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class CotizacionItem(Base):
    __tablename__ = "CotizacionesItems"

    __table_args__ = (
        UniqueConstraint("id_cotizacion", "id_producto", name="uq_producto_cotizacion_codigo"),
    )

    id_cotizacionitem = Column(Integer, primary_key=True)
    id_cotizacion = Column(Integer, ForeignKey("Cotizaciones.id_cotizacion"), nullable=False)
    cotizacion = relationship("Cotizacion")
    id_producto = Column(Integer, ForeignKey("Productos.id_producto"), nullable=False)
    producto = relationship("Producto")
    nombre_producto = Column(String(255), nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    cantidad = Column(Integer, nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)