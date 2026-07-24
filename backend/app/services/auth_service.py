from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.shared import Usuario
from app.core.security import verify_password
from fastapi.concurrency import run_in_threadpool
from typing import Optional


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[Usuario]:
    """
    Autentica un usuario por email y contraseña.
    """
    
    # Buscar usuario por email y estado activo
    result = await db.execute(
        select(Usuario)
        .where(
            Usuario.email == email,
            Usuario.estado == "activo"
        )
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        return None

    es_valido = await run_in_threadpool(verify_password, password, usuario.password_hash)
    
    if not es_valido:
        return None
    
    return usuario

