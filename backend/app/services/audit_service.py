"""
Utilidad ligera para registrar logs de auditoría.

Solo registra acciones de ESCRITURA importantes:
  - Crear / Editar / Eliminar cuentas bancarias
  - Crear / Editar / Eliminar usuarios
  - Actualizar configuración de empresa
  - Cambiar contraseña
  - Login (éxito y fallo)

NO registra lecturas (GET) para evitar saturar la tabla.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.shared import AuditGlobal
import logging

logger = logging.getLogger(__name__)


async def registrar_audit(
    db: AsyncSession,
    *,
    empresa_id: int,
    usuario_id: int,
    accion: str,
    tabla: str,
    registro_id: int | None = None,
    descripcion: str | None = None,
    cambios: str | None = None,
    ip_usuario: str | None = None,
) -> None:
    """
    Registra un evento de auditoría en audit_global.
    
    Uso:
        await registrar_audit(
            db,
            empresa_id=1,
            usuario_id=5,
            accion="crear_cuenta_bancaria",
            tabla="cuentas_bancarias",
            registro_id=12,
            descripcion="BCP Soles — 123456789",
        )
    """
    try:
        log = AuditGlobal(
            empresa_id=empresa_id,
            usuario_id=usuario_id,
            accion=accion,
            tabla=tabla,
            registro_id=registro_id,
            descripcion=descripcion,
            cambios=cambios,
            ip_usuario=ip_usuario,
        )
        db.add(log)
        await db.flush()  # flush, no commit — se commitea con la transacción principal
    except Exception as e:
        logger.warning(f"Error registrando audit log: {e}")
        # Nunca lanzar excepción por un audit log fallido
