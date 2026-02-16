from fastapi import APIRouter, Depends, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_user, get_tenant_db, CurrentUser
from app.services.empresa_service import obtener_configuracion, actualizar_configuracion
from app.services.logo_service import subir_logo, eliminar_logo
from app.services.usuario_service import (
    crear_usuario, obtener_usuario, actualizar_usuario, 
    eliminar_usuario, listar_usuarios,
    cambiar_password, obtener_mi_perfil, actualizar_mi_perfil
)
from app.schemas.empresa import ConfiguracionEmpresaResponse, UpdateConfiguracionEmpresaRequest
from app.schemas.usuarios import (
    createUsuarioRequest, updateUsuarioRequest, usuarioResponse,
    CambiarPasswordRequest, CambiarPasswordResponse,
    UpdateMiPerfilRequest, MiPerfilResponse
)

router = APIRouter(prefix="/api/empresa", tags=["Empresa"])


@router.get(
    "/configuracion",
    response_model=ConfiguracionEmpresaResponse,
    summary="Obtener configuración de empresa",
    description="Obtiene la configuración actual de la empresa."
)
async def get_configuracion(
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene la configuración de la empresa del usuario autenticado.
    
    Incluye:
    - Series de comprobantes (factura, boleta, NC, ND)
    - Ruta del certificado digital
    - Datos para PDF (logo, teléfono, email)
    """
    config = await obtener_configuracion(db, current_user.empresa_id)
    return config


@router.put(
    "/configuracion",
    response_model=ConfiguracionEmpresaResponse,
    summary="Actualizar configuración de empresa",
    description="Actualiza la configuración de la empresa."
)
async def update_configuracion(
    data: UpdateConfiguracionEmpresaRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Actualiza la configuración de la empresa.
    
    Solo se actualizan los campos enviados en el request.
    
    Ejemplo JSON:
    ```json
    {
        "serie_factura": "F002",
        "logo_url": "https://ejemplo.com/logo.png",
        "telefono": "01-234-5678",
        "email": "ventas@empresa.com"
    }
    ```
    """
    config = await actualizar_configuracion(db, current_user.empresa_id, data)
    return config


# ============================================================================
# LOGO DE EMPRESA
# ============================================================================

@router.post(
    "/logo",
    summary="Subir logo de empresa",
    description="Sube o reemplaza el logo de la empresa. Formatos: PNG, JPEG. Máx: 2MB. Dimensiones: 200-800px ancho, 80-400px alto."
)
async def post_logo(
    request: Request,
    file: UploadFile = File(..., description="Archivo de imagen (PNG o JPEG)"),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Sube o reemplaza el logo de la empresa.
    
    Validaciones:
    - Formato: PNG o JPEG
    - Tamaño: ≤ 2 MB
    - Dimensiones: ancho 200–800 px, alto 80–400 px
    - Dimensiones recomendadas: 400×150 px
    """
    base_url = str(request.base_url).rstrip("/")
    logo_url = await subir_logo(db, current_user.empresa_id, file, base_url)
    return {"logo_url": logo_url}


@router.delete(
    "/logo",
    summary="Eliminar logo de empresa",
    description="Elimina el logo de la empresa."
)
async def delete_logo(
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Elimina el logo de la empresa del sistema."""
    await eliminar_logo(db, current_user.empresa_id)
    return {"message": "Logo eliminado correctamente"}


@router.post("/usuarios", response_model=usuarioResponse)
async def post_usuario(
    data: createUsuarioRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Crea un nuevo usuario para la empresa.
    
    Solo el administrador puede crear usuarios.
    
    Roles válidos: administrador, contador, gerente_ventas, vendedor, operario, readonly
    
    Ejemplo JSON:
    ```json
    {
        "email": "vendedor@empresa.com",
        "nombre": "Juan",
        "apellido": "Pérez",
        "password": "Password123!",
        "rol": "vendedor"
    }
    ```
    """
    usuario = await crear_usuario(db, current_user.empresa_id, data, current_user)
    return usuario


@router.get("/usuarios", response_model=list[usuarioResponse])
async def get_usuarios(
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene la lista de usuarios de la empresa.
    """
    usuarios = await listar_usuarios(db, current_user.empresa_id, current_user)
    return usuarios


# ============================================================================
# MI PERFIL Y CAMBIAR CONTRASEÑA 
# ============================================================================

@router.get(
    "/usuarios/me",
    response_model=MiPerfilResponse,
    summary="Obtener mi perfil",
    description="Obtiene el perfil completo del usuario autenticado."
)
async def get_mi_perfil(
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Retorna los datos completos del perfil del usuario autenticado.
    
    Incluye: id, email, nombre, apellido, rol, estado, empresa_id, 
    created_at, ultimo_login
    """
    usuario = await obtener_mi_perfil(db, current_user.usuario_id)
    return usuario


@router.put(
    "/usuarios/me",
    response_model=MiPerfilResponse,
    summary="Actualizar mi perfil",
    description="Actualiza el perfil del usuario autenticado."
)
async def put_mi_perfil(
    data: UpdateMiPerfilRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Actualiza el nombre y/o apellido del usuario autenticado.
    
    Solo se actualizan los campos proporcionados.
    
    Ejemplo JSON:
    ```json
    {
        "nombre": "Juan Carlos",
        "apellido": "Pérez García"
    }
    ```
    """
    usuario = await actualizar_mi_perfil(db, current_user.usuario_id, data)
    return usuario


@router.put(
    "/usuarios/cambiar-password",
    response_model=CambiarPasswordResponse,
    summary="Cambiar contraseña propia",
    description="Permite al usuario autenticado cambiar su contraseña."
)
async def put_cambiar_password(
    data: CambiarPasswordRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Cambia la contraseña del usuario autenticado.
    
    Requisitos:
    - Proporcionar contraseña actual correcta
    - Nueva contraseña debe ser diferente a la actual
    - Nueva contraseña debe tener al menos 8 caracteres, 1 mayúscula y 1 número
    
    Ejemplo JSON:
    ```json
    {
        "password_actual": "Password123!",
        "password_nuevo": "NewPassword456!"
    }
    ```
    """
    await cambiar_password(db, current_user.usuario_id, data)
    return CambiarPasswordResponse()


# ============================================================================
# CRUD USUARIOS POR ID
# ============================================================================

@router.get("/usuarios/{id}", response_model=usuarioResponse)
async def get_usuario(
    id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene un usuario por su ID.
    """
    usuario = await obtener_usuario(db, id, current_user.empresa_id, current_user)
    return usuario


@router.put("/usuarios/{id}", response_model=usuarioResponse)
async def put_usuario(
    id: int,
    data: updateUsuarioRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Actualiza un usuario por su ID.
    
    Solo el administrador puede cambiar el rol.
    Usuarios pueden actualizar su propio nombre y apellido.
    
    Estados válidos: activo, inactivo, bloqueado
    Roles válidos: administrador, contador, gerente_ventas, vendedor, operario, readonly
    
    Ejemplo JSON:
    ```json
    {
        "nombre": "Juan Carlos",
        "apellido": "Pérez García",
        "rol": "gerente_ventas",
        "estado": "activo"
    }
    ```
    """
    usuario = await actualizar_usuario(db, id, current_user.empresa_id, data, current_user)
    return usuario


@router.delete("/usuarios/{id}", response_model=usuarioResponse)
async def delete_usuario(
    id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Elimina un usuario por su ID.
    """
    usuario = await eliminar_usuario(db, id, current_user.empresa_id, current_user)
    return usuario