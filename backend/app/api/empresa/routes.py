from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_user, get_tenant_db, CurrentUser
from app.services.empresa_service import obtener_configuracion, actualizar_configuracion
from app.services.usuario_service import crear_usuario, obtener_usuario, actualizar_usuario, eliminar_usuario, listar_usuarios
from app.schemas.empresa import ConfiguracionEmpresaResponse, UpdateConfiguracionEmpresaRequest
from app.schemas.usuarios import createUsuarioRequest, updateUsuarioRequest, usuarioResponse

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