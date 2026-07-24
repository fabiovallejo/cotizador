from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token
from app.core.dependencies import get_current_user, CurrentUser
from app.services.auth_service import authenticate_user
from app.services.password_reset_service import solicitar_reset_password, resetear_password
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.schemas.usuarios import (
    OlvidePasswordRequest, OlvidePasswordResponse,
    ResetearPasswordRequest, ResetearPasswordResponse
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
            "rol": user_data.rol,
            "nombre": user_data.nombre
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
        db_schema=current_user.db_schema,
        nombre=current_user.nombre
    )


# ============================================================================
# RECUPERAR CONTRASEÑA
# ============================================================================

@router.post(
    "/olvide-password",
    response_model=OlvidePasswordResponse,
    summary="Solicitar recuperación de contraseña",
    description="Genera un token de recuperación de contraseña."
)
async def post_olvide_password(
    data: OlvidePasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Solicita un token para restablecer la contraseña.
    
    SEGURIDAD: Siempre retorna éxito para evitar enumeración de emails.
    
    En desarrollo: Retorna el token directamente.
    En producción: El token se envía por email.
    
    Ejemplo JSON:
    ```json
    {
        "email": "usuario@empresa.com"
    }
    ```
    """
    result = await solicitar_reset_password(db, data)
    return OlvidePasswordResponse(**result)


@router.post(
    "/resetear-password/{token}",
    response_model=ResetearPasswordResponse,
    summary="Restablecer contraseña con token",
    description="Restablece la contraseña usando un token válido."
)
async def post_resetear_password(
    token: str,
    data: ResetearPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Restablece la contraseña usando el token recibido por email.
    
    Validaciones:
    - Token debe existir
    - Token no debe estar usado
    - Token no debe estar expirado (24 horas)
    - Nueva contraseña debe tener al menos 8 caracteres, 1 mayúscula y 1 número
    
    Ejemplo JSON:
    ```json
    {
        "password_nuevo": "NewPassword123!"
    }
    ```
    """
    result = await resetear_password(db, token, data)
    return ResetearPasswordResponse(**result)
