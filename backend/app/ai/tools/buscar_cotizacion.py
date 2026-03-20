from agents import function_tool, RunContextWrapper
from typing import Annotated, Optional
from sqlalchemy import select, text, or_

from app.ai.context import ChatContext
from app.core.database import AsyncSessionLocal
from app.models.tenant import Cotizacion

@function_tool
async def buscar_cotizacion(
    ctx: RunContextWrapper[ChatContext],
    numero: Annotated[Optional[str], "Número de cotización (ej: 'cot-2026-009', '2026-009' o '009')"] = None,
    cliente_id: Annotated[Optional[int], "ID del cliente"] = None,
    estado: Annotated[Optional[str], "Estado: borrador, enviada, aceptada, rechazada"] = None,
) -> str:
    """
    Busca cotizaciones por número, cliente o estado.
    Usa esta tool cuando el usuario mencione un código/número de cotización.
    """
    if not numero and not cliente_id and not estado:
        return "Debes especificar al menos un criterio: número, cliente_id o estado."

    async with AsyncSessionLocal() as session:
        await session.execute(
            text(f'SET search_path TO "{ctx.context.db_schema}", public')
        )

        stmt = select(Cotizacion).where(Cotizacion.deleted_at == None)

        if numero:
            # Limpiar número y buscar de forma flexible
            numero_limpio = numero.lower().replace("cot-", "").replace("-", "").strip()
            stmt = stmt.where(
                or_(
                    Cotizacion.numero_cotizacion.ilike(f"%{numero_limpio}%"),
                    Cotizacion.numero_cotizacion.ilike(f"%{numero}%")
                )
            )

        if cliente_id:
            stmt = stmt.where(Cotizacion.cliente_id == cliente_id)

        if estado:
            stmt = stmt.where(Cotizacion.estado == estado.lower())

        stmt = stmt.order_by(Cotizacion.created_at.desc()).limit(10)

        result = await session.execute(stmt)
        cotizaciones = result.scalars().all()

    if not cotizaciones:
        criterios = []
        if numero:
            criterios.append(f"número '{numero}'")
        if cliente_id:
            criterios.append(f"cliente ID {cliente_id}")
        if estado:
            criterios.append(f"estado '{estado}'")
        return f"No se encontraron cotizaciones con {' y '.join(criterios)}."

    # Si solo hay 1 resultado, formato detallado
    if len(cotizaciones) == 1:
        cot = cotizaciones[0]
        return f"""Cotización encontrada:

ID: {cot.id} | Número: {cot.numero_cotizacion} | Cliente ID: {cot.cliente_id} | Estado: {cot.estado.upper()} | Moneda: {cot.moneda} | Total: {cot.moneda} {float(cot.total):,.2f} | Vencimiento: {cot.fecha_vencimiento or 'N/A'}

Usa el ID {cot.id} para obtener detalles o actualizarla.""".strip()

    # Múltiples resultados: formato compacto
    lineas = []
    for cot in cotizaciones:
        lineas.append(
            f"• ID: {cot.id} | {cot.numero_cotizacion} | Cliente ID: {cot.cliente_id} | "
            f"Estado: {cot.estado.upper()} | Total: {cot.moneda} {float(cot.total):,.2f} | "
            f"Vence: {cot.fecha_vencimiento or 'N/A'}"
        )

    return f"Se encontraron {len(cotizaciones)} cotización(es):\n" + "\n".join(lineas)