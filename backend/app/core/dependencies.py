from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from app.core.database import AsyncSessionLocal
from app.core.security import decode_token
from app.models.shared import Empresa

security = HTTPBearer()


class CurrentUser:
    """Datos del usuario autenticado extraídos del JWT."""
    def __init__(self, usuario_id: int, empresa_id: int, rol: str, db_schema: str):
        self.usuario_id = usuario_id
        self.empresa_id = empresa_id
        self.rol = rol
        self.db_schema = db_schema


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """Extrae y valida el usuario del token JWT."""
    token = credentials.credentials
    payload = decode_token(token)
    
    usuario_id = payload.get("sub")
    empresa_id = payload.get("empresa_id")
    rol = payload.get("rol")
    
    if not usuario_id or not empresa_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token incompleto"
        )
    
    # Obtener el schema de la empresa
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Empresa.db_schema).where(Empresa.id == empresa_id)
        )
        db_schema = result.scalar_one_or_none()
        
        if not db_schema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa no encontrada"
            )
    
    return CurrentUser(
        usuario_id=int(usuario_id),
        empresa_id=int(empresa_id),
        rol=rol,
        db_schema=db_schema
    )


async def get_tenant_db(
    current_user: CurrentUser = Depends(get_current_user)
) -> AsyncGenerator[AsyncSession, None]:
    """
    Crea una sesión de BD con el search_path configurado al schema del tenant.
    """
    async with AsyncSessionLocal() as session:
        # Setear el search_path al schema del tenant
        await session.execute(
            text(f'SET search_path TO "{current_user.db_schema}", public')
        )
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
