from typing import Annotated, Optional
from agents import function_tool, RunContextWrapper
from sqlalchemy import select, text
from app.ai.context import ChatContext
from app.ai.http import get_internal_client
from app.core.database import AsyncSessionLocal
from app.models.tenant import Cliente


@function_tool
async def actualizar_cliente(
    ctx: RunContextWrapper[ChatContext],
    cliente_id: Annotated[int, "ID del cliente a actualizar (obtenido con buscar_cliente)"],
    razon_social: Annotated[Optional[str], "Nueva razon social"] = None,
    nombre_comercial: Annotated[Optional[str], "Nuevo nombre comercial"] = None,
    email: Annotated[Optional[str], "Nuevo email"] = None,
    telefono: Annotated[Optional[str], "Nuevo telefono"] = None,
    direccion_completa: Annotated[Optional[str], "Nueva direccion completa"] = None,
    ubigeo: Annotated[Optional[str], "Nuevo ubigeo"] = None,
    es_cliente_frecuente: Annotated[Optional[bool], "Si es cliente frecuente"] = None,
    estado: Annotated[Optional[str], "Nuevo estado (activo/inactivo)"] = None,
) -> str:
    """
    Actualiza los datos de un cliente existente.
    Solo se actualizan los campos proporcionados, el resto se conserva igual.
    Usar buscar_cliente primero para obtener el ID del cliente.
    """
    try:
        # Paso 1: obtener datos actuales del cliente directo desde la BD
        async with AsyncSessionLocal() as session:
            await session.execute(
                text(f'SET search_path TO "{ctx.context.db_schema}", public')
            )
            result = await session.execute(
                select(Cliente).where(
                    Cliente.id == cliente_id,
                    Cliente.deleted_at == None,
                )
            )
            actual = result.scalar_one_or_none()

        if actual is None:
            return f"No se encontro un cliente con ID {cliente_id}."

        # Paso 2: mezclar datos actuales con los cambios solicitados
        payload = {
            "tipo_documento":       actual.tipo_documento,
            "numero_documento":     actual.numero_documento,
            "razon_social":         razon_social        if razon_social        is not None else actual.razon_social,
            "nombre_comercial":     nombre_comercial    if nombre_comercial    is not None else actual.nombre_comercial,
            "email":                email               if email               is not None else actual.email,
            "telefono":             telefono            if telefono            is not None else actual.telefono,
            "direccion_completa":   direccion_completa  if direccion_completa  is not None else actual.direccion_completa,
            "ubigeo":               ubigeo              if ubigeo              is not None else actual.ubigeo,
            "es_cliente_frecuente": es_cliente_frecuente if es_cliente_frecuente is not None else actual.es_cliente_frecuente,
            "estado":               estado              if estado              is not None else actual.estado,
        }

        # Paso 3: enviar el PUT con todos los campos completos
        async with get_internal_client(ctx.context.token) as client:
            response = await client.put(
                f"/api/clientes/actualizar/{cliente_id}",
                json=payload,
            )

        if response.status_code == 404:
            return f"No se encontro un cliente con ID {cliente_id}."

        if response.status_code != 200:
            return (
                f"Error al actualizar el cliente ({response.status_code}): "
                f"{response.text}"
            )

    except Exception as e:
        return f"Error interno en la tool: {type(e).__name__}: {e}"

    cambios = {
        k: v for k, v in {
            "razon_social":         razon_social,
            "nombre_comercial":     nombre_comercial,
            "email":                email,
            "telefono":             telefono,
            "direccion_completa":   direccion_completa,
            "ubigeo":               ubigeo,
            "es_cliente_frecuente": es_cliente_frecuente,
            "estado":               estado,
        }.items() if v is not None
    }

    campos_txt = ", ".join(cambios.keys())
    data = response.json()
    return (
        f"Cliente actualizado correctamente.\n"
        f"  Cliente : {data.get('razon_social', '—')}\n"
        f"  Campos  : {campos_txt}"
    )