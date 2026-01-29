from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.tenant import Producto
from app.schemas.productos import ProductoRequest


async def crear_producto(db: AsyncSession, data: ProductoRequest) -> Producto:
    """Crea un nuevo producto en la base de datos."""
    
    # Verificar si ya existe un producto con ese código
    result = await db.execute(
        select(Producto).where(Producto.codigo == data.codigo)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un producto con el código {data.codigo}"
        )
    
    nuevo_producto = Producto(
        codigo=data.codigo,
        nombre=data.nombre,
        descripcion=data.descripcion,
        codigo_unspsc=data.codigo_unspsc,
        tipo=data.tipo,
        categoria=data.categoria,
        marca=data.marca,
        precio_unitario=data.precio_unitario,
        costo_unitario=data.costo_unitario,
        precio_distribuidor=data.precio_distribuidor,
        aplica_igv=data.aplica_igv,
        igv_porcentaje=data.igv_porcentaje,
        tipo_afectacion_igv=data.tipo_afectacion_igv,
        moneda=data.moneda,
        unidad_medida=data.unidad_medida,
        tiene_stock=data.tiene_stock,
        cantidad_stock=data.cantidad_stock,
        estado=data.estado
    )
    
    db.add(nuevo_producto)
    await db.commit()
    await db.refresh(nuevo_producto)
    
    return nuevo_producto
