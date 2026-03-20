from typing import Annotated, Optional
from agents import function_tool, RunContextWrapper
from app.ai.context import ChatContext
from app.ai.http import get_internal_client
from pydantic import BaseModel

class ItemCotizacion(BaseModel):
    producto_id: int
    cantidad: float

@function_tool
async def actualizar_cotizacion(
    ctx: RunContextWrapper[ChatContext],
    cotizacion_id: Annotated[int, "ID de la cotización a actualizar"],
    cliente_id: Annotated[Optional[int], "ID del cliente (si se quiere cambiar)"] = None,
    items: Annotated[Optional[list[ItemCotizacion]], (
        "Lista de productos. REEMPLAZA todos los items existentes. "
        "Para eliminar items: no incluirlos en el array. "
        "Para agregar: incluirlos. Ejemplo: [{'producto_id': 3, 'cantidad': 2}]"
    )] = None,
    moneda: Annotated[Optional[str], "Moneda: PEN o USD (si se quiere cambiar)"] = None,
    vigencia_dias: Annotated[Optional[int], "Días de vigencia (si se quiere cambiar)"] = None,
    terminos_condiciones: Annotated[Optional[str], "Términos y condiciones"] = None,
    forma_pago: Annotated[Optional[str], "Forma de pago"] = None,
    lugar_entrega: Annotated[Optional[str], "Lugar de entrega"] = None,
    tiempo_entrega: Annotated[Optional[str], "Tiempo de entrega"] = None,
    notas_internas: Annotated[Optional[str], "Notas internas"] = None,
) -> str:
    """
    Actualiza una cotización existente.
    IMPORTANTE: Solo funciona si la cotización está en estado BORRADOR.
    El agente DEBE primero llamar obtener_cotizacion para ver items actuales
    antes de actualizar, especialmente si va a modificar items.
    """
    # Construir payload solo con los campos que se van a actualizar
    payload = {}
    
    if cliente_id is not None:
        payload["cliente_id"] = cliente_id
    if items is not None:
        payload["items"] = [item.model_dump() for item in items]
    if moneda is not None:
        payload["moneda"] = moneda
    if vigencia_dias is not None:
        payload["vigencia_dias"] = vigencia_dias
    if terminos_condiciones is not None:
        payload["terminos_condiciones"] = terminos_condiciones
    if forma_pago is not None:
        payload["forma_pago"] = forma_pago
    if lugar_entrega is not None:
        payload["lugar_entrega"] = lugar_entrega
    if tiempo_entrega is not None:
        payload["tiempo_entrega"] = tiempo_entrega
    if notas_internas is not None:
        payload["notas_internas"] = notas_internas

    # Validar que haya al menos un campo a actualizar
    if not payload:
        return "No se especificó ningún campo para actualizar. Indica qué deseas cambiar."

    try:
        async with get_internal_client(ctx.context.token) as client:
            response = await client.put(f"/api/cotizaciones/{cotizacion_id}", json=payload)

        if response.status_code == 400:
            error_detail = response.json().get('detail', response.text)
            # Detectar si es error de estado
            if "borrador" in error_detail.lower():
                return (
                    f"No se puede editar la cotización (ID {cotizacion_id}): solo se pueden "
                    "editar cotizaciones en estado BORRADOR.\n\n"
                    "Si necesitas modificar una cotización enviada/aceptada, debes crear una nueva."
                )
            return f"Error de validación: {error_detail}"

        if response.status_code == 404:
            return f"No existe cotización con ID {cotizacion_id}."

        if response.status_code == 500:
            error_detail = response.json().get('detail', response.text)
            if "TC" in error_detail or "SUNAT" in error_detail:
                return (
                    "No se pudo actualizar: el servicio de tipo de cambio de SUNAT "
                    "no está disponible en este momento.\n\n"
                    "Esto ocurre cuando hay productos en diferentes monedas. "
                    "Intenta nuevamente en unos minutos."
                )
            return f"Error del servidor: {error_detail}"

        if response.status_code != 200:
            return f"Error inesperado ({response.status_code}): {response.text}"

    except Exception as e:
        return f"Error de conexión: {type(e).__name__}: {e}"

    data = response.json()

    # Construir resumen de cambios
    cambios = []
    if cliente_id is not None:
        cambios.append(f"Cliente → ID {cliente_id}")
    if items is not None:
        cambios.append(f"Productos → {len(items)} item(s)")
    if moneda is not None:
        cambios.append(f"Moneda → {moneda}")
    if vigencia_dias is not None:
        cambios.append(f"Vigencia → {vigencia_dias} días")
    if forma_pago is not None:
        cambios.append(f"Forma de pago → {forma_pago}")
    if lugar_entrega is not None:
        cambios.append(f"Lugar de entrega → {lugar_entrega}")
    if tiempo_entrega is not None:
        cambios.append(f"Tiempo de entrega → {tiempo_entrega}")

    cambios_str = "\n  • ".join(cambios) if cambios else "Campos varios"

    # Obtener items actualizados si se modificaron
    items_txt = ""
    if items is not None:
        try:
            async with get_internal_client(ctx.context.token) as client:
                items_response = await client.get(f"/api/cotizaciones/{cotizacion_id}/items")
                if items_response.status_code == 200:
                    items_data = items_response.json()
                    items_txt = "\n".join(
                        f"  {i+1}. Producto ID {item['producto_id']} × {float(item['cantidad'])} = "
                        f"{data.get('moneda', '')} {float(item['total']):,.2f}"
                        for i, item in enumerate(items_data)
                    )
        except:
            # Si falla obtener items, usar los que se enviaron
            items_txt = "\n".join(
                f"  {i+1}. Producto ID {it['producto_id']} × {it['cantidad']}"
                for i, it in enumerate([item.model_dump() for item in items])
            )

    return f"""
Cotización #{data.get('numero_cotizacion', cotizacion_id)} actualizada exitosamente.

Cambios aplicados:
  • {cambios_str}

Resumen actual:
  Cliente ID    : {data.get('cliente_id', '—')}
  Moneda        : {data.get('moneda', '—')}
  Subtotal      : {data.get('moneda', '')} {float(data.get('subtotal', 0)):,.2f}
  IGV           : {data.get('moneda', '')} {float(data.get('igv_total', 0)):,.2f}
  Total         : {data.get('moneda', '')} {float(data.get('total', 0)):,.2f}
  Estado        : {data.get('estado', '—').upper()}
  Vencimiento   : {data.get('fecha_vencimiento', '—')}
  Forma de pago : {data.get('forma_pago', 'N/A')}

{f"Productos actualizados:{chr(10)}{items_txt}" if items_txt else ""}

La cotización sigue en BORRADOR y puede seguir editándose.
""".strip()