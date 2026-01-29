from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.tenant import Cliente
from app.schemas.clientes import ClienteRequest


async def crear_cliente(db: AsyncSession, data: ClienteRequest) -> Cliente:
    """Crea un nuevo cliente en la base de datos."""
    
    # Verificar si ya existe un cliente con ese número de documento
    result = await db.execute(
        select(Cliente).where(Cliente.numero_documento == data.numero_documento)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un cliente con el {data.tipo_documento} {data.numero_documento}"
        )
    
    nuevo_cliente = Cliente(
        tipo_documento=data.tipo_documento,
        numero_documento=data.numero_documento,
        razon_social=data.razon_social,
        nombre_comercial=data.nombre_comercial,
        email=data.email,
        telefono=data.telefono,
        direccion_completa=data.direccion_completa,
        ubigeo=data.ubigeo,
        es_cliente_frecuente=data.es_cliente_frecuente,
        estado=data.estado
    )
    
    db.add(nuevo_cliente)
    await db.commit()
    await db.refresh(nuevo_cliente)
    
    return nuevo_cliente
