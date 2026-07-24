from agents import function_tool, RunContextWrapper
from typing import Annotated
from sqlalchemy import select, text

from app.ai.context import ChatContext
from app.core.database import AsyncSessionLocal
from app.models.tenant import Cliente

@function_tool
async def buscar_cliente(
    ctx: RunContextWrapper[ChatContext],
    query: Annotated[str, "Nombre, DNI o RUC del cliente a buscar"]
) -> str:
    """Busca clientes por nombre, DNI o RUC y devuelve una lista resumida."""
    async with AsyncSessionLocal() as session:
        await session.execute(
            text(f'SET search_path TO "{ctx.context.db_schema}", public')
        )

        # Si el query es numérico (DNI/RUC), buscar coincidencia exacta
        if query.strip().isdigit():
            stmt = select(Cliente).where(
                Cliente.deleted_at == None,
                Cliente.numero_documento == query.strip()
            )
        else:
            # Búsqueda parcial por nombre o razón social
            stmt = select(Cliente).where(
                Cliente.deleted_at == None,
                (Cliente.razon_social.ilike(f"%{query}%")) |
                (Cliente.nombre_comercial.ilike(f"%{query}%"))
            ).limit(10)

        result = await session.execute(stmt)
        clientes = result.scalars().all()

    if not clientes:
        return "No se encontraron clientes con ese criterio."

    lineas = []
    for c in clientes:
        lineas.append(
            f"• | ID: {c.id} | {c.razon_social} | {c.tipo_documento}: {c.numero_documento} | Nombre Comercial: {c.nombre_comercial or 'N/A'} "
            f"Email: {c.email or 'N/A'} | Tel: {c.telefono or 'N/A'} | Direccion: {c.direccion_completa or 'N/A'} | Es Cliente Frecuente: {c.es_cliente_frecuente} | Estado: {c.estado}"
        )
    return f"Se encontraron {len(clientes)} cliente(s):\n" + "\n".join(lineas)