from agents import function_tool, RunContextWrapper
from typing import Annotated
from app.ai.context import ChatContext
from app.ai.http import get_internal_client


@function_tool
async def obtener_reporte_productos_top(
    ctx: RunContextWrapper[ChatContext],
    fecha_inicio: Annotated[str, "Fecha de inicio del reporte (YYYY-MM-DD)"],
    fecha_fin: Annotated[str, "Fecha de fin del reporte (YYYY-MM-DD)"],
) -> str:
    """
    Obtiene el ranking de productos mas vendidos en un periodo:
    ingresos, margen, tasa de conversion y alertas por producto.
    """
    try:
        async with get_internal_client(ctx.context.token) as client:
            response = await client.get(
                "/api/reportes/productos-top",
                params={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
            )

        if response.status_code != 200:
            return f"Error al obtener el reporte ({response.status_code}): {response.text}"

    except Exception as e:
        return f"Error interno en la tool: {type(e).__name__}: {e}"

    data      = response.json()
    productos = data["productos"]
    alertas   = data["alertas"]

    productos_txt = "\n".join(
        f"  {i+1}. [{p['codigo']}] {p['nombre']}\n"
        f"     Ingresos: S/ {p['ingresos']:,.2f} ({p['porcentaje_total']}% del total)"
        f" | Cantidad: {p['cantidad_vendida']}\n"
        f"     Conversion: {p['tasa_conversion']}%"
        f" ({p['cotizaciones_cerradas']}/{p['total_cotizaciones']} cot.)"
        f" | Monto sin cerrar: S/ {p['monto_no_cerrado']:,.2f}"
        + (f"\n     Margen estimado: S/ {p['margen']:,.2f}" if p["margen"] is not None else "")
        for i, p in enumerate(productos)
    ) or "  (sin productos en el periodo)"

    alertas_txt = "\n".join(
        f"  {a['tipo'].upper()} — {a['mensaje']}"
        for a in alertas
    ) or "  (sin alertas)"

    return f"""
REPORTE PRODUCTOS TOP — {fecha_inicio} al {fecha_fin}
{"=" * 55}

RESUMEN
  Total ingresos   : S/ {data['total_ingresos']:,.2f}
  Total productos  : {data['total_productos']}

RANKING
{productos_txt}

ALERTAS
{alertas_txt}
""".strip()