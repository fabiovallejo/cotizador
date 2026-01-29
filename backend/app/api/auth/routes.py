from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token
from app.core.dependencies import get_current_user, CurrentUser
from app.services.auth_service import authenticate_user
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse


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


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener usuario actual"
)
async def get_me(
    current_user: CurrentUser = Depends(get_current_user)
):
    """Retorna los datos del usuario autenticado."""
    return UserResponse(
        usuario_id=current_user.usuario_id,
        empresa_id=current_user.empresa_id,
        rol=current_user.rol,
        db_schema=current_user.db_schema
    )
