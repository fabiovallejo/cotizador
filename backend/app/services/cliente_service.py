from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.tenant import Cliente
from app.schemas.clientes import ClienteRequest
from typing import Optional


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


async def listar_clientes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    estado: Optional[str] = None,
    busqueda: Optional[str] = None
) -> list[Cliente]:
    """Lista clientes con paginación y filtros opcionales."""
    
    query = select(Cliente).where(Cliente.deleted_at == None)
    
    if estado:
        query = query.where(Cliente.estado == estado)
    
    if busqueda:
        query = query.where(
            (Cliente.razon_social.ilike(f"%{busqueda}%")) |
            (Cliente.numero_documento.ilike(f"%{busqueda}%")) |
            (Cliente.nombre_comercial.ilike(f"%{busqueda}%"))
        )
    
    query = query.offset(skip).limit(limit).order_by(Cliente.razon_social)
    
    result = await db.execute(query)
    return result.scalars().all()


async def actualizar_cliente(
    db: AsyncSession,
    id: int,
    data: ClienteRequest
) -> Cliente:
    """Actualiza un cliente existente"""
    cliente = await db.get(Cliente, id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    cliente.tipo_documento = data.tipo_documento
    cliente.numero_documento = data.numero_documento
    cliente.razon_social = data.razon_social
    cliente.nombre_comercial = data.nombre_comercial
    cliente.email = data.email
    cliente.telefono = data.telefono
    cliente.direccion_completa = data.direccion_completa
    cliente.ubigeo = data.ubigeo
    cliente.es_cliente_frecuente = data.es_cliente_frecuente
    cliente.estado = data.estado

    await db.commit()
    await db.refresh(cliente)

    return cliente
