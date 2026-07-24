from agents import function_tool, RunContextWrapper
from typing import Annotated
from app.ai.context import ChatContext
from app.ai.http import get_internal_client

@function_tool
async def obtener_reporte_clientes(
    ctx: RunContextWrapper[ChatContext],
    fecha_inicio: Annotated[str, "Fecha de inicio del reporte (YYYY-MM-DD)"],
    fecha_fin: Annotated[str, "Fecha de fin del reporte (YYYY-MM-DD)"],
) -> str:
    """
    Obtiene el reporte de clientes en un periodo: segmentacion VIP/Regular,
    ticket promedio, historial, clientes inactivos y alertas.
    """
    try:
        async with get_internal_client(ctx.context.token) as client:
            response = await client.get(
                "/api/reportes/clientes",
                params={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
            )

        if response.status_code != 200:
            return f"Error al obtener el reporte ({response.status_code}): {response.text}"

    except Exception as e:
        return f"Error interno en la tool: {type(e).__name__}: {e}"

    data     = response.json()
    clientes = data["clientes"]
    alertas  = data["alertas"]

    # Separar VIP y regulares para mejor lectura
    vip      = [c for c in clientes if c["segmento"] == "VIP"]
    regulares = [c for c in clientes if c["segmento"] == "Regular"]

    def _fmt_cliente(c: dict) -> str:
        inactivo_txt = f" | INACTIVO {c['dias_inactivo']} dias" if c["es_inactivo"] else ""
        return (
            f"  {c['razon_social']} ({c['tipo_documento']}: {c['numero_documento']})\n"
            f"     Monto: S/ {c['monto_total']:,.2f}"
            f" | Ticket prom.: S/ {c['ticket_promedio']:,.2f}"
            f" | Cotizaciones: {c['total_cotizaciones']}"
            f" | Historico: S/ {c['monto_historico']:,.2f}"
            f"{inactivo_txt}"
        )

    vip_txt = "\n".join(_fmt_cliente(c) for c in vip) or "  (ninguno)"

    # Mostrar max 10 regulares para no saturar el contexto
    regulares_txt = "\n".join(
        _fmt_cliente(c) for c in regulares[:10]
    ) or "  (ninguno)"
    omitidos = len(regulares) - 10
    regulares_footer = (
        f"\n  ... y {omitidos} cliente(s) regular(es) mas no mostrados."
        if omitidos > 0 else ""
    )

    alertas_txt = "\n".join(
        f"  {a['tipo'].upper()} — {a['mensaje']}"
        for a in alertas
    ) or "  (sin alertas)"

    return f"""
REPORTE CLIENTES — {fecha_inicio} al {fecha_fin}
{"=" * 55}

RESUMEN
  Total clientes   : {data['total_clientes']}
  Inactivos        : {data['inactivos']}
  Promedio global  : S/ {data['promedio_global']:,.2f}
  Umbral VIP       : S/ {data['umbral_vip']:,.2f}

CLIENTES VIP ({len(vip)})
{vip_txt}

CLIENTES REGULARES ({len(regulares)})
{regulares_txt}{regulares_footer}

ALERTAS
{alertas_txt}
""".strip()