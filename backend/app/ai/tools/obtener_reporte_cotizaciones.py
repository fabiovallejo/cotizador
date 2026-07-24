from agents import function_tool, RunContextWrapper
from typing import Annotated, Optional
from app.ai.context import ChatContext
from app.ai.http import get_internal_client


@function_tool
async def obtener_reporte_cotizaciones(
    ctx: RunContextWrapper[ChatContext],
    fecha_inicio: Annotated[str, "Fecha de inicio del reporte (YYYY-MM-DD)"],
    fecha_fin: Annotated[str, "Fecha de fin del reporte (YYYY-MM-DD)"],
    vendedor_id: Annotated[Optional[int], "ID del vendedor para filtrar (opcional)"] = None,
    cliente_id:  Annotated[Optional[int], "ID del cliente para filtrar (opcional)"] = None,
) -> str:
    """
    Obtiene el reporte de cotizaciones en un periodo: metricas agregadas,
    alertas automaticas y detalle de cada cotizacion.
    Permite filtrar por vendedor y/o cliente.
    """
    import sys
    print(f"[TOOL] obtener_reporte_cotizaciones fecha_inicio={fecha_inicio} fecha_fin={fecha_fin}", flush=True)
    sys.stdout.flush()

    try:
        params: dict = {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
        if vendedor_id:
            params["vendedor_id"] = vendedor_id
        if cliente_id:
            params["cliente_id"] = cliente_id

        async with get_internal_client(ctx.context.token) as client:
            response = await client.get(
                "/api/reportes/cotizaciones",
                params=params,
            )

        print(f"[TOOL] status={response.status_code}", flush=True)

        if response.status_code != 200:
            return f"Error al obtener el reporte ({response.status_code}): {response.text}"

    except Exception as e:
        print(f"[TOOL] EXCEPCION: {type(e).__name__}: {e}", flush=True)
        return f"Error interno en la tool: {type(e).__name__}: {e}"

    data     = response.json()
    metricas = data["metricas"]
    alertas  = data["alertas"]
    detalle  = data["detalle"]

    alertas_txt = "\n".join(
        f"  {a['tipo'].upper()} — {a['mensaje']}"
        for a in alertas
    ) or "  (sin alertas)"

    detalle_txt = "\n".join(
        f"  #{d['numero']} | {d['cliente']} | {d['vendedor']}"
        f" | {d['moneda']} {d['total']:,.2f} | {d['estado']} | {d['fecha']}"
        for d in detalle[:20]
    ) or "  (sin cotizaciones en el periodo)"

    omitidas       = len(detalle) - 20
    detalle_footer = (
        f"\n  ... y {omitidas} cotizacion(es) mas no mostradas."
        if omitidas > 0 else ""
    )

    return f"""
REPORTE DE COTIZACIONES — {fecha_inicio} al {fecha_fin}
{"=" * 55}

METRICAS
  Total cotizaciones   : {metricas['total_cotizaciones']}
  Monto total          : S/ {metricas['monto_total']:,.2f}
  Valor promedio       : S/ {metricas['valor_promedio']:,.2f}
  Porcentaje aceptadas : {metricas['porcentaje_aceptadas']}%
  Tasa conversion      : {metricas['tasa_conversion']}%
  Tasa rechazo         : {metricas['tasa_rechazo']}%
  Pendientes >7 dias   : {metricas['pendientes']}
  Monto en riesgo      : S/ {metricas['monto_perdido']:,.2f}

ALERTAS
{alertas_txt}

DETALLE ({len(detalle)} cotizaciones)
{detalle_txt}{detalle_footer}
""".strip()