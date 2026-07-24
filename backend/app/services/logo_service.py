"""
Servicio para gestión de logo de empresa.

Maneja la subida, validación y eliminación del logo corporativo.
El logo se guarda en disco y la URL se almacena en Empresa.logo_url.
"""

import os
import shutil
import logging
from pathlib import Path
from io import BytesIO

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from PIL import Image

from app.models.shared import Empresa

logger = logging.getLogger(__name__)

# ── Constantes de validación ──
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MIN_WIDTH, MAX_WIDTH = 200, 800
MIN_HEIGHT, MAX_HEIGHT = 80, 400
UPLOAD_BASE = Path("uploads/logos")


def _get_extension(filename: str) -> str:
    """Extrae la extensión en minúsculas."""
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


async def subir_logo(
    db: AsyncSession,
    empresa_id: int,
    file: UploadFile,
    base_url: str,
) -> str:
    """
    Sube el logo de la empresa.

    Validaciones:
    - Formato: PNG o JPEG
    - Tamaño: ≤ 2 MB
    - Dimensiones: 200–800 px de ancho, 80–400 px de alto

    Retorna la URL pública del logo.
    """
    # 1. Validar extensión
    ext = _get_extension(file.filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no permitido. Solo se aceptan: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 2. Leer contenido y validar tamaño
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo excede el tamaño máximo de {MAX_FILE_SIZE // (1024*1024)} MB"
        )

    # 3. Validar dimensiones con Pillow
    try:
        img = Image.open(BytesIO(content))
        width, height = img.size
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo procesar la imagen. Asegúrate de que sea un archivo PNG o JPEG válido."
        )

    if not (MIN_WIDTH <= width <= MAX_WIDTH):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El ancho debe estar entre {MIN_WIDTH} y {MAX_WIDTH} px. Tu imagen tiene {width} px de ancho."
        )
    if not (MIN_HEIGHT <= height <= MAX_HEIGHT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El alto debe estar entre {MIN_HEIGHT} y {MAX_HEIGHT} px. Tu imagen tiene {height} px de alto."
        )

    # 4. Guardar archivo en disco
    # Normalizar extensión: jpg -> jpg (mantener)
    save_ext = "png" if ext == "png" else "jpg"
    empresa_dir = UPLOAD_BASE / str(empresa_id)
    empresa_dir.mkdir(parents=True, exist_ok=True)

    # Limpiar logos anteriores
    for old_file in empresa_dir.glob("logo.*"):
        old_file.unlink(missing_ok=True)

    file_path = empresa_dir / f"logo.{save_ext}"
    with open(file_path, "wb") as f:
        f.write(content)

    # 5. Construir URL pública
    logo_url = f"{base_url}/uploads/logos/{empresa_id}/logo.{save_ext}"

    # 6. Actualizar Empresa.logo_url
    result = await db.execute(
        select(Empresa).where(Empresa.id == empresa_id)
    )
    empresa = result.scalar_one_or_none()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    empresa.logo_url = logo_url
    await db.commit()

    logger.info(f"Logo subido para empresa_id={empresa_id}: {logo_url}")
    return logo_url


async def eliminar_logo(
    db: AsyncSession,
    empresa_id: int,
) -> None:
    """Elimina el logo de la empresa del disco y la base de datos."""
    # 1. Eliminar archivos del disco
    empresa_dir = UPLOAD_BASE / str(empresa_id)
    if empresa_dir.exists():
        shutil.rmtree(empresa_dir, ignore_errors=True)

    # 2. Limpiar Empresa.logo_url
    result = await db.execute(
        select(Empresa).where(Empresa.id == empresa_id)
    )
    empresa = result.scalar_one_or_none()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    empresa.logo_url = None
    await db.commit()

    logger.info(f"Logo eliminado para empresa_id={empresa_id}")
