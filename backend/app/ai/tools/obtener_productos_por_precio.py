from typing import Annotated, Optional
from agents import function_tool, RunContextWrapper
from sqlalchemy import text
from app.ai.context import ChatContext
from app.core.database import AsyncSessionLocal


@function_tool
async def obtener_productos_por_precio(
    ctx: RunContextWrapper[ChatContext],
    orden: Annotated[str, "Criterio de orden: 'asc' para los mas baratos, 'desc' para los mas caros"],
    limite: Annotated[int, "Cantidad de productos a retornar por moneda. Por defecto 5."] = 5,
    moneda: Annotated[Optional[str], "Filtrar por moneda especifica: PEN o USD. Si no se indica, se muestra el ranking separado por cada moneda."] = None,
    categoria: Annotated[Optional[str], "Filtrar por categoria (opcional)"] = None,
) -> str:
    """
    Retorna el ranking de productos ordenados por precio unitario.
    Usar orden='asc' para los mas baratos, orden='desc' para los mas caros.
    Si no se especifica moneda, devuelve el ranking separado por PEN y USD
    para evitar comparaciones incorrectas entre divisas.
    """
    if orden not in ("asc", "desc"):
        return "Error: el parametro orden debe ser 'asc' o 'desc'."

    etiqueta = "MAS CAROS" if orden == "desc" else "MAS BARATOS"

    # Determinar las monedas a consultar
    monedas = [moneda.upper()] if moneda else ["PEN", "USD"]

    filtros_base = [
        "deleted_at IS NULL",
        "estado = 'activo'",
        "precio_unitario IS NOT NULL",
    ]
    if categoria:
        filtros_base.append("categoria ILIKE :categoria")

    where_clause = " AND ".join(filtros_base)

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(
                text(f'SET search_path TO "{ctx.context.db_schema}", public')
            )

            resultados = {}
            for m in monedas:
                sql = text(f"""
                    SELECT
                        id,
                        codigo,
                        nombre,
                        categoria,
                        marca,
                        precio_unitario,
                        moneda,
                        unidad_medida,
                        tiene_stock,
                        cantidad_stock
                    FROM productos
                    WHERE {where_clause}
                      AND moneda = :moneda
                    ORDER BY precio_unitario {orden.upper()}
                    LIMIT :limite
                """)
                params: dict = {"moneda": m, "limite": limite}
                if categoria:
                    params["categoria"] = f"%{categoria}%"

                rows = (await session.execute(sql, params)).fetchall()
                if rows:
                    resultados[m] = rows

    except Exception as e:
        return f"Error interno en la tool: {type(e).__name__}: {e}"

    if not resultados:
        return "No se encontraron productos con los filtros indicados."

    # Formatear secciones por moneda
    secciones = []
    for m, rows in resultados.items():
        productos_txt = "\n".join(
            f"  {i+1}. [{r.codigo}] {r.nombre}\n"
            f"     Precio: {r.moneda} {float(r.precio_unitario):,.2f}"
            f" | Categoria: {r.categoria or 'N/A'}"
            f" | Marca: {r.marca or 'N/A'}"
            f" | Unidad: {r.unidad_medida}"
            + (f" | Stock: {r.cantidad_stock}" if r.tiene_stock else " | Sin control de stock")
            for i, r in enumerate(rows)
        )
        secciones.append(
            f"TOP {limite} {etiqueta} EN {m}\n"
            f"{'-' * 40}\n"
            f"{productos_txt}"
        )

    cabecera = f"TOP {limite} PRODUCTOS {etiqueta}"
    if categoria:
        cabecera += f" | Categoria: {categoria}"

    return f"""
{cabecera}
{"=" * 50}

{chr(10) + chr(10).join(secciones)}
""".strip()