from app.schemas.usuarios import UpdateMiPerfilRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from app.models.shared import Usuario
from app.core.security import hash_password, verify_password
from app.schemas.usuarios import createUsuarioRequest, updateUsuarioRequest
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def crear_usuario(
    db: AsyncSession,
    empresa_id: int,
    data: createUsuarioRequest,
    current_user: Usuario  # Debe ser administrador
) -> Usuario:
    """
    Crea nuevo usuario en la empresa.
    Solo administrador puede crear usuarios.
    """
    
    # 1. Validar que current_user es administrador
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden crear usuarios"
        )
    
    # 2. Validar que current_user pertenece a la empresa
    if current_user.empresa_id != empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes crear usuarios en otra empresa"
        )
    
    # 3. Verificar email no existe
    existe = await db.execute(
        select(Usuario).where(Usuario.email == data.email)
    )
    if existe.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ya registrado"
        )
    
    # 4. Hashear contraseña
    password_hash = await run_in_threadpool(hash_password, data.password)
    
    # 5. Crear usuario
    nuevo_usuario = Usuario(
        empresa_id=empresa_id,
        email=data.email,
        password_hash=password_hash,
        nombre=data.nombre,
        apellido=data.apellido,
        rol=data.rol,
        estado="activo"
    )
    
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)
    
    logger.info(f"Usuario creado: {nuevo_usuario.email} en empresa {empresa_id}")
    
    return nuevo_usuario


async def listar_usuarios(
    db: AsyncSession,
    empresa_id: int,
    current_user: Usuario
) -> list[Usuario]:
    """
    Lista todos los usuarios de la empresa
    Solo el administrador puede listar usuarios
    """
    if current_user.empresa_id != empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes listar usuarios de otra empresa"
        )

    if current_user.rol == "admin":
        usuarios = await db.execute(
            select(Usuario).where(Usuario.empresa_id == current_user.empresa_id)
        )
    else:
        usuarios = await db.execute(
            select(Usuario).where(Usuario.id == current_user.id)
        )
    
    return usuarios.scalars().all()



async def obtener_usuario(
    db: AsyncSession,
    id: int,
    empresa_id: int,
    current_user: Usuario
) -> Usuario:
    """
    Obtiene un usuario por su ID
    Solo el administrador puede obtener usuarios
    """
    if current_user.empresa_id != empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes obtener usuarios de otra empresa"
        )

    usuario = await db.execute(
        select(Usuario).where(Usuario.id == id, Usuario.empresa_id == empresa_id)
    )
    usuario = usuario.scalar_one_or_none()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    if current_user.rol != "admin" and current_user.id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes ver otros usuarios"
        )  
    
    return usuario


async def actualizar_usuario(
    db: AsyncSession,
    id: int,
    empresa_id: int,
    data: updateUsuarioRequest,
    current_user: Usuario
) -> Usuario:
    """
    Actualiza un usuario por su ID
    Solo el administrador puede actualizar usuarios
    """
    if current_user.empresa_id != empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes actualizar usuarios de otra empresa"
        )

    usuario = await obtener_usuario(db, id, empresa_id, current_user)

    if current_user.rol != "administrador" and current_user.id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes actualizar otros usuarios"
        )

    if data.nombre:
        usuario.nombre = data.nombre
    if data.apellido is not None:
        usuario.apellido = data.apellido
    if data.estado:
        usuario.estado = data.estado

    if data.rol and current_user.rol == "admin":
        usuario.rol = data.rol
    
    await db.commit()
    await db.refresh(usuario)
    
    return usuario


async def eliminar_usuario(
    db: AsyncSession,
    id: int,
    empresa_id: int,
    current_user: Usuario
) -> Usuario:
    """
    Elimina un usuario por su ID
    Solo el administrador puede eliminar usuarios
    """
    if current_user.empresa_id != empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes eliminar usuarios de otra empresa"
        )

    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden eliminar a otros usuarios"
        )  

    if current_user.usuario_id == id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario"
        )

    usuario = await obtener_usuario(db, id, empresa_id, current_user)

    usuario.estado = "inactivo"
    usuario.deleted_at = datetime.now()

    await db.commit()
    await db.refresh(usuario)
    
    return usuario


# ============================================================================
# CAMBIAR CONTRASEÑA
# ============================================================================

async def cambiar_password(
    db: AsyncSession,
    usuario_id: int,
    data  # CambiarPasswordRequest - evita import circular
) -> Usuario:
    """
    Cambia la contraseña del usuario autenticado.
    
    Validaciones:
    - Verifica la contraseña actual
    - La nueva contraseña debe ser diferente (validado en schema)
    """
    # Obtener usuario
    result = await db.execute(
        select(Usuario).where(Usuario.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar contraseña actual (en threadpool, es bloqueante)
    es_correcto = await run_in_threadpool(
        verify_password,
        data.password_actual,
        usuario.password_hash
    )
    
    if not es_correcto:
        logger.warning(f"Intento fallido de cambio de contraseña para: {usuario.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    # Hash nueva contraseña
    nuevo_hash = await run_in_threadpool(hash_password, data.password_nuevo)
    usuario.password_hash = nuevo_hash
    
    await db.commit()
    await db.refresh(usuario)
    
    logger.warning(f"Cambio de contraseña exitoso para usuario: {usuario.email}")
    
    return usuario


# ============================================================================
# MI PERFIL
# ============================================================================

async def obtener_mi_perfil(
    db: AsyncSession,
    usuario_id: int
) -> Usuario:
    """
    Obtiene el perfil completo del usuario autenticado.
    """
    result = await db.execute(
        select(Usuario).where(Usuario.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return usuario


async def actualizar_mi_perfil(
    db: AsyncSession,
    usuario_id: int,
    data: UpdateMiPerfilRequest
) -> Usuario:
    """
    Actualiza el perfil del usuario autenticado.
    
    Solo puede actualizar:
    - nombre
    - apellido
    """
    result = await db.execute(
        select(Usuario).where(Usuario.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Actualizar solo campos proporcionados
    if data.nombre is not None:
        usuario.nombre = data.nombre
    if data.apellido is not None:
        usuario.apellido = data.apellido
    
    await db.commit()
    await db.refresh(usuario)
    
    logger.info(f"Perfil actualizado para usuario: {usuario.email}")
    
    return usuario