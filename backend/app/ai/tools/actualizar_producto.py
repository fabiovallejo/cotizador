from typing import Annotated, Optional
from agents import function_tool, RunContextWrapper
from sqlalchemy import select, text
from app.ai.context import ChatContext
from app.ai.http import get_internal_client
from app.core.database import AsyncSessionLocal
from app.models.tenant import Producto


@function_tool
async def actualizar_producto(
    ctx: RunContextWrapper[ChatContext],
    producto_id: Annotated[int, "ID del producto a actualizar (obtenido con buscar_producto)"],
    nombre: Annotated[Optional[str], "Nuevo nombre"] = None,
    codigo: Annotated[Optional[str], "Nuevo codigo"] = None,
    descripcion: Annotated[Optional[str], "Nueva descripcion"] = None,
    tipo: Annotated[Optional[str], "Nuevo tipo"] = None,
    categoria: Annotated[Optional[str], "Nueva categoria"] = None,
    marca: Annotated[Optional[str], "Nueva marca"] = None,
    precio_unitario: Annotated[Optional[float], "Nuevo precio unitario"] = None,
    costo_unitario: Annotated[Optional[float], "Nuevo costo unitario"] = None,
    precio_distribuidor: Annotated[Optional[float], "Nuevo precio distribuidor"] = None,
    aplica_igv: Annotated[Optional[bool], "Nuevo aplica igv"] = None,
    igv_porcentaje: Annotated[Optional[float], "Nuevo igv porcentaje"] = None,
    moneda: Annotated[Optional[str], "Nueva moneda (PEN, USD, etc.)"] = None,
    unidad_medida: Annotated[Optional[str], "Nueva unidad medida"] = None,
    tiene_stock: Annotated[Optional[bool], "Nuevo tiene stock"] = None,
    cantidad_stock: Annotated[Optional[int], "Nuevo cantidad stock"] = None,
    estado: Annotated[Optional[str], "Nuevo estado (activo/inactivo)"] = None,
) -> str:
    """
    Actualiza los datos de un producto existente.
    Solo se actualizan los campos proporcionados, el resto se conserva igual.
    Usar buscar_producto primero para obtener el ID del producto.
    """
    def _float(val):
        """Convierte Decimal de SQLAlchemy a float serializable por JSON."""
        return float(val) if val is not None else None

    try:
        # Paso 1: obtener datos actuales del producto directo desde la BD
        async with AsyncSessionLocal() as session:
            await session.execute(
                text(f'SET search_path TO "{ctx.context.db_schema}", public')
            )
            result = await session.execute(
                select(Producto).where(
                    Producto.id == producto_id,
                    Producto.deleted_at == None,
                )
            )
            actual = result.scalar_one_or_none()

        if actual is None:
            return f"No se encontro un producto con ID {producto_id}."

        # Paso 2: mezclar datos actuales con los cambios solicitados
        # — campos de sistema (codigo_unspsc, tipo_afectacion_igv) se conservan
        #   siempre desde la BD sin exponerlos al agente
        # — campos numéricos se convierten a float para evitar Decimal no serializable
        payload = {
            "nombre":              nombre              if nombre              is not None else actual.nombre,
            "codigo":              codigo              if codigo              is not None else actual.codigo,
            "descripcion":         descripcion         if descripcion         is not None else actual.descripcion,
            "codigo_unspsc":       actual.codigo_unspsc,
            "tipo":                tipo                if tipo                is not None else actual.tipo,
            "categoria":           categoria           if categoria           is not None else actual.categoria,
            "marca":               marca               if marca               is not None else actual.marca,
            "precio_unitario":     precio_unitario     if precio_unitario     is not None else _float(actual.precio_unitario),
            "costo_unitario":      costo_unitario      if costo_unitario      is not None else _float(actual.costo_unitario),
            "precio_distribuidor": precio_distribuidor if precio_distribuidor is not None else _float(actual.precio_distribuidor),
            "aplica_igv":          aplica_igv          if aplica_igv          is not None else actual.aplica_igv,
            "igv_porcentaje":      igv_porcentaje      if igv_porcentaje      is not None else _float(actual.igv_porcentaje),
            "tipo_afectacion_igv": actual.tipo_afectacion_igv,
            "moneda":              moneda              if moneda              is not None else actual.moneda,
            "unidad_medida":       unidad_medida       if unidad_medida       is not None else actual.unidad_medida,
            "tiene_stock":         tiene_stock         if tiene_stock         is not None else actual.tiene_stock,
            "cantidad_stock":      cantidad_stock      if cantidad_stock      is not None else actual.cantidad_stock,
            "estado":              estado              if estado              is not None else actual.estado,
        }

        # Paso 3: enviar el PUT con todos los campos completos
        async with get_internal_client(ctx.context.token) as client:
            response = await client.put(
                f"/api/productos/actualizar/{producto_id}",
                json=payload,
            )

        if response.status_code == 404:
            return f"No se encontro un producto con ID {producto_id}."

        if response.status_code != 200:
            return (
                f"Error al actualizar el producto ({response.status_code}): "
                f"{response.text}"
            )

    except Exception as e:
        import traceback
        print(f"[TOOL actualizar_producto] ERROR: {type(e).__name__}: {e}", flush=True)
        print(traceback.format_exc(), flush=True)
        return f"Error interno en la tool: {type(e).__name__}: {e}"

    cambios = {
        k: v for k, v in {
            "nombre":              nombre,
            "codigo":              codigo,
            "descripcion":         descripcion,
            "tipo":                tipo,
            "categoria":           categoria,
            "marca":               marca,
            "precio_unitario":     precio_unitario,
            "costo_unitario":      costo_unitario,
            "precio_distribuidor": precio_distribuidor,
            "aplica_igv":          aplica_igv,
            "igv_porcentaje":      igv_porcentaje,
            "moneda":              moneda,
            "unidad_medida":       unidad_medida,
            "tiene_stock":         tiene_stock,
            "cantidad_stock":      cantidad_stock,
            "estado":              estado,
        }.items() if v is not None
    }

    campos_txt = ", ".join(cambios.keys())
    data = response.json()
    return (
        f"Producto actualizado correctamente.\n"
        f"  Producto : {data.get('nombre', '—')}\n"
        f"  Campos   : {campos_txt}"
    )