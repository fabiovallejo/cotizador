"""
Servicio para recuperación de contraseña.

Flujo:
1. Usuario solicita reset -> genera token
2. Token enviado por email (en producción)
3. Usuario usa token para cambiar contraseña
4. Token marcado como usado
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from datetime import datetime, timedelta
import secrets
import logging

from app.models.shared import Usuario, PasswordResetToken
from app.core.security import hash_password
from app.schemas.usuarios import OlvidePasswordRequest, ResetearPasswordRequest

logger = logging.getLogger(__name__)


async def solicitar_reset_password(
    db: AsyncSession,
    data: OlvidePasswordRequest
) -> dict:
    """
    Genera un token de reset para el email proporcionado.
    
    SEGURIDAD: Siempre retorna éxito para evitar enumeración de emails.
    """
    # Buscar usuario por email
    result = await db.execute(
        select(Usuario).where(Usuario.email == data.email)
    )
    usuario = result.scalar_one_or_none()
    
    # Si no existe, retornar éxito igual (seguridad)
    if not usuario:
        logger.warning(f"Reset password solicitado para email no existente: {data.email}")
        return {
            "mensaje": "Si el email existe, recibirá instrucciones",
            "token": None
        }
    
    # Verificar usuario activo
    if usuario.estado != "activo":
        logger.warning(f"Reset password solicitado para usuario inactivo: {data.email}")
        return {
            "mensaje": "Si el email existe, recibirá instrucciones",
            "token": None
        }
    
    # Generar token seguro
    token = secrets.token_urlsafe(32)
    
    # Crear registro de token (expira en 24 horas)
    token_obj = PasswordResetToken(
        usuario_id=usuario.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    
    db.add(token_obj)
    await db.commit()
    
    logger.warning(f"Reset password token generado para: {data.email}")
    
    # TODO: En producción, enviar email con el token
    # await enviar_email_reset(usuario.email, token)
    
    return {
        "mensaje": "Si el email existe, recibirá instrucciones",
        "token": token  # Solo en desarrollo, quitar en producción
    }


async def validar_token_reset(
    db: AsyncSession,
    token: str
) -> PasswordResetToken:
    """
    Valida que el token sea válido, no usado y no expirado.
    
    Raises:
        HTTPException: Si token inválido, usado o expirado
    """
    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token == token)
    )
    token_obj = result.scalar_one_or_none()
    
    if not token_obj:
        logger.error(f"Intento con token inválido: {token[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido"
        )
    
    if token_obj.used_at:
        logger.error(f"Intento de reusar token para usuario_id: {token_obj.usuario_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token ya utilizado"
        )
    
    if token_obj.expires_at < datetime.utcnow():
        logger.error(f"Token expirado para usuario_id: {token_obj.usuario_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado"
        )
    
    return token_obj


async def resetear_password(
    db: AsyncSession,
    token: str,
    data: ResetearPasswordRequest
) -> dict:
    """
    Restablece la contraseña usando un token válido.
    
    1. Valida el token
    2. Cambia la contraseña
    3. Marca el token como usado
    """
    # Validar token
    token_obj = await validar_token_reset(db, token)
    
    # Obtener usuario
    result = await db.execute(
        select(Usuario).where(Usuario.id == token_obj.usuario_id)
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no encontrado"
        )
    
    # Guardar email antes del commit (evita lazy-loading después del commit)
    usuario_email = usuario.email
    
    # Hashear nueva contraseña
    nuevo_hash = await run_in_threadpool(hash_password, data.password_nuevo)
    usuario.password_hash = nuevo_hash
    
    # Marcar token como usado
    token_obj.used_at = datetime.utcnow()
    
    await db.commit()
    
    logger.warning(f"Contraseña restablecida para usuario: {usuario_email}")
    
    return {"mensaje": "Contraseña restablecida correctamente"}
