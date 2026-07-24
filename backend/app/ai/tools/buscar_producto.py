from agents import function_tool, RunContextWrapper
from typing import Annotated
from sqlalchemy import select, text

from app.ai.context import ChatContext
from app.core.database import AsyncSessionLocal
from app.models.tenant import Producto    


@function_tool
async def buscar_producto(
    ctx: RunContextWrapper[ChatContext],
    query: Annotated[str, "Código/SKU, nombre, categoría o marca del producto a buscar"]
) -> str:
    """Busca productos por código/SKU (exacto) o por nombre, categoría, marca (parcial)."""
    async with AsyncSessionLocal() as session:
        await session.execute(
            text(f'SET search_path TO "{ctx.context.db_schema}", public')
        )

        # Intentar coincidencia exacta por código/SKU primero
        stmt_exacto = select(Producto).where(
            Producto.deleted_at == None,
            Producto.codigo == query.strip()
        )
        result = await session.execute(stmt_exacto)
        productos = result.scalars().all()

        # Si no hay match exacto, buscar por nombre, descripción, categoría o marca
        if not productos:
            stmt = select(Producto).where(
                Producto.deleted_at == None,
                (Producto.nombre.ilike(f"%{query}%")) |
                (Producto.descripcion.ilike(f"%{query}%")) |
                (Producto.categoria.ilike(f"%{query}%")) |
                (Producto.marca.ilike(f"%{query}%"))
            ).limit(10)
            result = await session.execute(stmt)
            productos = result.scalars().all()

    if not productos:
        return "No se encontraron productos con ese criterio."

    lineas = []
    for p in productos:
        stock_info = f"Stock: {p.cantidad_stock}" if p.tiene_stock else "Sin control de stock"
        igv_info = f"IGV: {p.igv_porcentaje}%" if p.aplica_igv else "No aplica IGV"
        lineas.append(
            f"• ID: {p.id} | Código: [{p.codigo}] | Nombre: {p.nombre} | Tipo: {p.tipo} | Categoría: {p.categoria or 'N/A'} | Marca: {p.marca or 'N/A'}\n"
            f"  Descripción: {p.descripcion or 'N/A'}\n"
            f"  Precio: {p.precio_unitario} {p.moneda} | Costo: {p.costo_unitario or 'N/A'} | Precio Distribuidor: {p.precio_distribuidor or 'N/A'}\n"
            f"  {igv_info} | Unidad: {p.unidad_medida} | {stock_info} | Estado: {p.estado}"
        )
    return f"Se encontraron {len(productos)} producto(s):\n" + "\n".join(lineas)