from typing import Annotated
from agents import function_tool, RunContextWrapper
from app.ai.context import ChatContext
from app.ai.http import get_internal_client

@function_tool
async def obtener_cotizacion(
    ctx: RunContextWrapper[ChatContext],
    cotizacion_id: Annotated[int, "ID de la cotización a obtener"],
) -> str:
    """
    Obtiene los detalles completos de una cotización específica incluyendo sus items.
    Usa esta tool antes de actualizar para verificar el estado actual.
    """
    try:
        async with get_internal_client(ctx.context.token) as client:
            # Obtener cotización
            response = await client.get(f"/api/cotizaciones/{cotizacion_id}")

            if response.status_code == 404:
                return f"No existe cotización con ID {cotizacion_id}."

            if response.status_code == 500:
                error_detail = response.json().get('detail', response.text)
                return f"Error del servidor: {error_detail}"

            if response.status_code != 200:
                return f"Error inesperado ({response.status_code}): {response.text}"

            cot = response.json()

            # Obtener items de la cotización
            items_response = await client.get(f"/api/cotizaciones/{cotizacion_id}/items")
            
            items = []
            if items_response.status_code == 200:
                items = items_response.json()

    except Exception as e:
        return f"Error de conexión: {type(e).__name__}: {e}"

    # Formatear items
    items_txt = ""
    if items:
        items_lineas = []
        for i, item in enumerate(items, 1):
            items_lineas.append(
                f"  {i}. Producto ID {item['producto_id']} — "
                f"{float(item['cantidad'])} ud. × {cot['moneda']} {float(item['precio_unitario']):,.2f} = "
                f"{cot['moneda']} {float(item['total']):,.2f}"
            )
        items_txt = "\n".join(items_lineas)
    else:
        items_txt = "  (sin items)"

    return f"""Cotización #{cot['numero_cotizacion']} (ID: {cot['id']})

Estado        : {cot['estado'].upper()}
Cliente ID    : {cot['cliente_id']}
Moneda        : {cot['moneda']}
Vigencia      : {cot['vigencia_dias']} días
Vencimiento   : {cot.get('fecha_vencimiento', 'N/A')}

Subtotal      : {cot['moneda']} {float(cot['subtotal']):,.2f}
IGV           : {cot['moneda']} {float(cot['igv_total']):,.2f}
Total         : {cot['moneda']} {float(cot['total']):,.2f}

Forma de pago : {cot.get('forma_pago', 'N/A')}
Lugar entrega : {cot.get('lugar_entrega', 'N/A')}
Tiempo entrega: {cot.get('tiempo_entrega', 'N/A')}

Productos:
{items_txt}

Términos: {cot.get('terminos_condiciones', 'N/A')}
Notas internas: {cot.get('notas_internas') or '(ninguna)'}""".strip()