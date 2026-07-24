from agents import function_tool, RunContextWrapper
from typing import Annotated
from sqlalchemy import select, text

from app.ai.context import ChatContext
from app.core.database import AsyncSessionLocal
from app.models.tenant import Cliente  
from typing import Optional

@function_tool
async def crear_cliente(
    ctx: RunContextWrapper[ChatContext],
    tipo_documento: Annotated[str, "Tipo de documento del cliente"],
    numero_documento: Annotated[str, "Número de documento del cliente"],
    razon_social: Annotated[str, "Razón social del cliente"],
    nombre_comercial: Optional[Annotated[str, "Nombre comercial del cliente"]] = None,
    email: Optional[Annotated[str, "Email del cliente"]] = None,
    telefono: Optional[Annotated[str, "Teléfono del cliente"]] = None,
    direccion_completa: Optional[Annotated[str, "Dirección completa del cliente"]] = None,
    ubigeo: Optional[Annotated[str, "Ubigeo del cliente"]] = None,
    es_cliente_frecuente: Annotated[bool, "Indica si el cliente es frecuente"] = False,
    estado: Annotated[str, "Estado del cliente"] = "activo",
) -> str:
    """Crea un nuevo cliente en el sistema."""
    async with AsyncSessionLocal() as session:
        await session.execute(
            text(f'SET search_path TO "{ctx.context.db_schema}", public')
        )
        cliente = Cliente(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            razon_social=razon_social,
            nombre_comercial=nombre_comercial,
            email=email,
            telefono=telefono,
            direccion_completa=direccion_completa,
            ubigeo=ubigeo,
            es_cliente_frecuente=es_cliente_frecuente,
            estado=estado,
        )
        session.add(cliente)
        await session.commit()
        await session.refresh(cliente)
        return f"Cliente creado exitosamente: {cliente.razon_social}"