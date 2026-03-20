from agents import function_tool, RunContextWrapper
from typing import Annotated
from app.ai.context import ChatContext
from app.ai.http import get_internal_client


@function_tool
async def obtener_dashboard_ejecutivo(
    ctx: RunContextWrapper[ChatContext],
    periodo: Annotated[int, "Periodo en dias a analizar (7, 30 o 90). Por defecto 30."] = 30,
) -> str:
    """
    Obtiene el dashboard ejecutivo completo: KPIs con variacion vs periodo anterior,
    cotizaciones pendientes, serie diaria, top productos, productos problematicos,
    clientes inactivos y ranking de vendedores.
    """
    import sys
    print(f"[TOOL] iniciando...", flush=True)
    try:
        print(f"[TOOL] token prefix={ctx.context.token[:20]}", flush=True)
        async with get_internal_client(ctx.context.token) as client:
            print(f"[TOOL] cliente creado, haciendo request...", flush=True)
            response = await client.get(
                "/api/reportes/dashboard",
                params={"periodo": periodo},
            )
            print(f"[TOOL] status={response.status_code}", flush=True)
            print(f"[TOOL] body={response.text[:500]}", flush=True)

    except Exception as e:
        print(f"[TOOL] EXCEPCION: {type(e).__name__}: {e}", flush=True)
        return f"Error interno en la tool: {type(e).__name__}: {e}"
    
    if response.status_code != 200:
        return f"Error al obtener el dashboard ({response.status_code}): {response.text}"

    data = response.json()
    kpis = data["kpis"]
    c    = kpis["cotizaciones"]
    t    = kpis["tasa_conversion"]
    ing  = kpis["ingresos"]
    al   = kpis["alertas"]

    pendientes_txt = "\n".join(
        f"  #{p['numero']} | {p['cliente']} | S/ {p['monto']:,.2f}"
        f" | {p['dias']} dias | {p['vendedor']}"
        for p in data["cotizaciones_pendientes"]
    ) or "  (ninguna)"

    top_prod_txt = "\n".join(
        f"  {i+1}. {p['nombre']} ({p['codigo']})"
        f" — S/ {p['ingresos']:,.2f} | Conversion: {p['tasa_conversion']}%"
        for i, p in enumerate(data["top_productos"])
    ) or "  (sin datos)"

    prob_prod_txt = "\n".join(
        f"  {p['nombre']}"
        f" — Perdida potencial: S/ {p['monto_perdido']:,.2f} | Conversion: {p['tasa_conversion']}%"
        for p in data["productos_problematicos"]
    ) or "  (ninguno)"

    inactivos_txt = "\n".join(
        f"  {c['razon_social']}"
        f" — Ultima cot.: {c['ultima_cotizacion']} ({c['dias']} dias)"
        f" | Historico: S/ {c['monto_historico']:,.2f}"
        for c in data["clientes_inactivos"]
    ) or "  (ninguno)"

    vendedores_txt = "\n".join(
        f"  {i+1}. {v['nombre']}"
        f" — {v['cerradas']}/{v['cotizaciones']} cerradas ({v['tasa_conversion']}%)"
        f" | S/ {v['monto']:,.2f}"
        for i, v in enumerate(data["top_vendedores"])
    ) or "  (sin datos)"

    ticket_prom = ing["ticket_promedio"]

    return f"""
DASHBOARD EJECUTIVO — Ultimos {data['periodo_dias']} dias
{"=" * 50}

KPIS
  Cotizaciones : {c['valor']} ({c['variacion']:+.1f}% vs periodo anterior)
  Ingresos     : S/ {ing['valor']:,.2f} ({ing['variacion']:+.1f}% vs periodo anterior)
  Tasa conv.   : {t['valor']}% ({t['aceptadas']} de {t['total']} | {t['variacion']:+.1f}pp vs anterior)
  Ticket prom. : S/ {ticket_prom:,.2f}

ALERTAS
  Cotizaciones pendientes +7 dias : {al['pendientes']}
  Clientes inactivos +30 dias     : {al['inactivos']}

COTIZACIONES PENDIENTES (top 5)
{pendientes_txt}

SERIE DIARIA
  {len(data['serie_diaria'])} dias con actividad registrada

TOP 5 PRODUCTOS
{top_prod_txt}

PRODUCTOS PROBLEMATICOS (conversion < 50%)
{prob_prod_txt}

CLIENTES INACTIVOS (top 5)
{inactivos_txt}

RANKING VENDEDORES
{vendedores_txt}
""".strip()