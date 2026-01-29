from app.schemas.auth import TokenResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token
from app.services.auth_service import authenticate_user
from app.schemas.auth import (
    LoginRequest, TokenResponse
)


router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="Autentica un usuario y retorna un JWT token"
)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    user_data = await authenticate_user(db, credentials.email, credentials.password)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token JWT
    access_token = create_access_token(
        data={
            "sub": str(user_data.id),
            "empresa_id": user_data.empresa_id,
            "rol": user_data.rol
        }
    )
    
    return {
            "access_token": access_token,
            "token_type": "bearer"
        }
