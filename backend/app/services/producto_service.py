from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.tenant import Producto
from app.schemas.productos import ProductoRequest
from typing import Optional
from datetime import datetime

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


async def listar_productos(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    estado: Optional[str] = None,
    busqueda: Optional[str] = None
) -> list[Producto]:
    """Lista productos con filtros opcionales."""
    query = select(Producto).where(Producto.deleted_at == None)

    if estado:
        query = query.where(Producto.estado == estado)

    if busqueda:
        query = query.where(
            (Producto.nombre.ilike(f"%{busqueda}%")) |
            (Producto.codigo.ilike(f"%{busqueda}%")) 
        )
    query = query.offset(skip).limit(limit).order_by(Producto.nombre)

    result = await db.execute(query)
    return result.scalars().all()


async def actualizar_producto(
    db: AsyncSession,
    id: int,
    data: ProductoRequest
) -> Producto:
    """Actualiza un producto existente"""
    producto = await db.get(Producto, id)
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    # Actualizar campos
    producto.codigo = data.codigo
    producto.nombre = data.nombre
    producto.descripcion = data.descripcion
    producto.codigo_unspsc = data.codigo_unspsc
    producto.tipo = data.tipo
    producto.categoria = data.categoria
    producto.marca = data.marca
    producto.precio_unitario = data.precio_unitario
    producto.costo_unitario = data.costo_unitario
    producto.precio_distribuidor = data.precio_distribuidor
    producto.aplica_igv = data.aplica_igv
    producto.igv_porcentaje = data.igv_porcentaje
    producto.tipo_afectacion_igv = data.tipo_afectacion_igv
    producto.moneda = data.moneda
    producto.unidad_medida = data.unidad_medida
    producto.tiene_stock = data.tiene_stock
    producto.cantidad_stock = data.cantidad_stock
    producto.estado = data.estado

    await db.commit()
    await db.refresh(producto)

    return producto


async def eliminar_producto(db: AsyncSession, id: int) -> Producto:
    """Elimina un producto existente (soft delete)"""
    producto = await db.get(Producto, id)
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    producto.deleted_at = datetime.now()
    await db.commit()
    await db.refresh(producto)

    return producto
