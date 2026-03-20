from agents import function_tool, RunContextWrapper
from typing import Annotated
from sqlalchemy import select, text

from app.ai.context import ChatContext
from app.core.database import AsyncSessionLocal
from app.models.tenant import Producto    
from typing import Optional


@function_tool
async def crear_producto(
    ctx: RunContextWrapper[ChatContext],
    codigo: Annotated[str, "Código/SKU del producto"],
    nombre: Annotated[str, "Nombre del producto"],
    precio_unitario: Annotated[float, "Precio unitario del producto"],
    descripcion: Optional[Annotated[str, "Descripción del producto"]] = None,
    categoria: Optional[Annotated[str, "Categoría del producto"]] = None,
    marca: Optional[Annotated[str, "Marca del producto"]] = None,
    moneda: Annotated[str, "Moneda del producto"] = "PEN",
    costo_unitario: Optional[Annotated[float, "Costo unitario del producto"]] = None,
    precio_distribuidor: Optional[Annotated[float, "Precio distribuidor del producto"]] = None,
    aplica_igv: Annotated[bool, "Indica si el producto aplica IGV"] = True,
    unidad_medida: Annotated[str, "Unidad de medida del producto"] = "UND",
    tiene_stock: Annotated[bool, "Indica si el producto tiene stock"] = True,
    cantidad_stock: Optional[Annotated[int, "Cantidad en stock del producto"]] = None,
    estado: Annotated[str, "Estado del producto"] = "activo",
) -> str:
    """Crea un nuevo producto en el sistema."""
    async with AsyncSessionLocal() as session:
        await session.execute(
            text(f'SET search_path TO "{ctx.context.db_schema}", public')
        )
        producto = Producto(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            categoria=categoria,
            marca=marca,
            precio_unitario=precio_unitario,
            moneda=moneda,
            costo_unitario=costo_unitario,
            precio_distribuidor=precio_distribuidor,
            aplica_igv=aplica_igv,
            unidad_medida=unidad_medida,
            tiene_stock=tiene_stock,
            cantidad_stock=cantidad_stock,
            estado=estado,
        )
        session.add(producto)
        await session.commit()
        await session.refresh(producto)
        return f"Producto creado exitosamente: {producto.nombre}"