from typing import Annotated, Optional
from agents import function_tool, RunContextWrapper
from app.ai.context import ChatContext
from app.ai.http import get_internal_client
from pydantic import BaseModel

class ItemCotizacion(BaseModel):
    producto_id: int
    cantidad: float

@function_tool
async def crear_cotizacion_borrador(
    ctx: RunContextWrapper[ChatContext],
    cliente_id: Annotated[int, "ID del cliente (obtenido con buscar_cliente)"],
    items: Annotated[list[ItemCotizacion], (
        "Lista de productos a cotizar. Cada item debe tener: "
        "producto_id (int, obtenido con buscar_producto) y cantidad (float). "
        "Ejemplo: [{'producto_id': 3, 'cantidad': 2}, {'producto_id': 7, 'cantidad': 1}]"
    )],
    moneda: Annotated[str, "Moneda de la cotizacion: PEN o USD"] = "PEN",
    vigencia_dias: Annotated[int, "Dias de vigencia de la cotizacion. Por defecto 30."] = 30,
    terminos_condiciones: Annotated[Optional[str], (
        "Terminos y condiciones. Si el usuario no indica, usar: "
        "'Precios validos por {vigencia_dias} dias. Sujeto a disponibilidad de stock.'"
    )] = None,
    forma_pago: Annotated[Optional[str], (
        "Forma de pago. Para crear la cotizacion el valor DEBE SER EXACTAMENTE uno de los siguientes: 'contado', "
        "'credito_7', 'credito_15', 'credito_30', 'credito_60', 'credito_90', "
        "'50_orden_50_contra_entrega'. Si el usuario no indica, usar: 'contado'"
        "Tener en cuenta por ejemplo: si el usuario indica credito a 30 dias, el valor debe ser 'credito_30'"
    )] = None,
    lugar_entrega: Annotated[Optional[str], (
        "Lugar de entrega. Si el usuario no indica, usar: 'A coordinar con el cliente'"
    )] = None,
    tiempo_entrega: Annotated[Optional[str], (
        "Tiempo de entrega. Si el usuario no indica, usar: 'A coordinar'"
    )] = None,
    notas_internas: Annotated[Optional[str], "Notas internas visibles solo para el equipo (opcional)"] = None,
) -> str:
    """
    Crea una cotizacion en estado borrador.
    IMPORTANTE: antes de llamar esta tool, el agente debe tener confirmacion
    del usuario con el resumen completo de la cotizacion a crear.
    Requiere cliente_id e items como minimo. El resto tiene valores por defecto.
    """
    # Aplicar defaults si el usuario no especifico
    terminos_condiciones = (
        terminos_condiciones
        or f"Precios validos por {vigencia_dias} dias. Sujeto a disponibilidad de stock."
    )
    forma_pago     = forma_pago     or "contado"
    lugar_entrega  = lugar_entrega  or "A coordinar con el cliente"
    tiempo_entrega = tiempo_entrega or "A coordinar"

    # Convertir items a diccionarios
    items_dict = [item.model_dump() for item in items]

    payload = {
        "cliente_id":           cliente_id,
        "moneda":               moneda,
        "vigencia_dias":        vigencia_dias,
        "terminos_condiciones": terminos_condiciones,
        "forma_pago":           forma_pago,
        "lugar_entrega":        lugar_entrega,
        "tiempo_entrega":       tiempo_entrega,
        "notas_internas":       notas_internas,
        "items":                items_dict,  # Enviar como dicts
    }

    try:
        async with get_internal_client(ctx.context.token) as client:
            response = await client.post("/api/cotizaciones/crear", json=payload)

        if response.status_code == 400:
            error_detail = response.json().get('detail', response.text)
            return f"No se pudo crear la cotización: {error_detail}\n\nVerifica los datos e intenta nuevamente."

        if response.status_code == 500:
            error_detail = response.json().get('detail', response.text)
            if "TC" in error_detail or "SUNAT" in error_detail:
                return (
                    "No se pudo crear la cotización: el servicio de tipo de cambio de SUNAT "
                    "no está disponible en este momento.\n\n"
                    "Esto ocurre cuando hay productos en diferentes monedas (PEN/USD). "
                    "Puedes intentar nuevamente en unos minutos."
                )
            return f"Error del servidor: {error_detail}"

        if response.status_code != 201:
            return f"Error inesperado ({response.status_code}): {response.text}"

    except Exception as e:
        return f"Error de conexión: {type(e).__name__}: {e}"

    data = response.json()

    # Ahora items_dict son diccionarios
    items_txt = "\n".join(
        f"  - Producto ID {it['producto_id']} x {it['cantidad']}"
        for it in items_dict
    )

    return f"""
Cotizacion creada exitosamente en estado BORRADOR.

  Numero        : {data.get('numero_cotizacion', '—')}
  Cliente ID    : {cliente_id}
  Moneda        : {moneda}
  Subtotal      : {moneda} {float(data.get('subtotal', 0)):,.2f}
  IGV           : {moneda} {float(data.get('igv_total', 0)):,.2f}
  Total         : {moneda} {float(data.get('total', 0)):,.2f}
  Vigencia      : {vigencia_dias} dias
  Vencimiento   : {data.get('fecha_vencimiento', '—')}
  Forma de pago : {forma_pago}
  Lugar entrega : {lugar_entrega}
  Tiempo entrega: {tiempo_entrega}

  Productos:
{items_txt}

La cotizacion fue creada en borrador. El usuario puede revisarla y enviarla desde el sistema.
""".strip()