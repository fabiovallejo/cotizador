from typing import Annotated
from agents import function_tool, RunContextWrapper
from app.ai.context import ChatContext
from app.ai.http import get_internal_client

@function_tool
async def cambiar_estado_cotizacion(
    ctx: RunContextWrapper[ChatContext],
    cotizacion_id: Annotated[int, "ID de la cotización"],
    nuevo_estado: Annotated[str, (
        "Nuevo estado. Valores válidos: 'enviada', 'aceptada', 'rechazada'. "
        "Transiciones: borrador→enviada, enviada→aceptada o rechazada"
    )],
) -> str:
    """
    Cambia el estado de una cotización.
    IMPORTANTE: El agente debe llamar obtener_cotizacion primero para verificar
    el estado actual y confirmar con el usuario antes de cambiar estados críticos
    como 'aceptada' o 'rechazada'.
    """
    # Validar estados permitidos
    estados_validos = ["enviada", "aceptada", "rechazada"]
    if nuevo_estado.lower() not in estados_validos:
        return (
            f"Estado '{nuevo_estado}' no válido. "
            f"Estados permitidos: {', '.join(estados_validos)}"
        )

    payload = {"estado": nuevo_estado.lower()}

    try:
        async with get_internal_client(ctx.context.token) as client:
            response = await client.patch(
                f"/api/cotizaciones/{cotizacion_id}/estado",
                json=payload
            )

        if response.status_code == 400:
            error_detail = response.json().get('detail', response.text)
            # Detectar errores de transición de estado
            if "transición" in error_detail.lower() or "estado" in error_detail.lower():
                return (
                    f"Transición de estado inválida: {error_detail}\n\n"
                    "Transiciones válidas:\n"
                    "  • borrador → enviada\n"
                    "  • enviada → aceptada o rechazada"
                )
            return f"Error de validación: {error_detail}"

        if response.status_code == 404:
            return f"No existe cotización con ID {cotizacion_id}."

        if response.status_code == 500:
            error_detail = response.json().get('detail', response.text)
            return f"Error del servidor: {error_detail}"

        if response.status_code != 200:
            return f"Error inesperado ({response.status_code}): {response.text}"

    except Exception as e:
        return f"Error de conexión: {type(e).__name__}: {e}"

    data = response.json()
    estado_nuevo = data.get('estado', nuevo_estado).upper()

    # Mensajes según el nuevo estado
    mensajes = {
        "enviada": "La cotización fue enviada al cliente. Ahora espera su respuesta.",
        "aceptada": "Cotización aceptada. El cliente confirmó la compra.",
        "rechazada": "La cotización fue rechazada por el cliente.",
    }
    mensaje_extra = mensajes.get(nuevo_estado.lower(), "")

    return f"""
Estado de cotización #{data.get('numero_cotizacion', cotizacion_id)} actualizado.

  Estado nuevo   : {estado_nuevo}
  Cliente        : ID {data.get('cliente_id', '—')}
  Total          : {data.get('moneda', '')} {float(data.get('total', 0)):,.2f}
  Vencimiento    : {data.get('fecha_vencimiento', '—')}

{mensaje_extra}
""".strip()