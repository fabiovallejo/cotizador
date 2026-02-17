from app.core.dependencies import CurrentUser, get_current_user, get_tenant_db
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.productos import ProductoRequest, ProductoResponse
from app.services.producto_service import crear_producto, listar_productos, actualizar_producto, eliminar_producto

router = APIRouter(prefix="/api/productos", tags=["Productos"])

@router.post(
    "/crear",
    response_model=ProductoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto"
)
async def crear(
    data: ProductoRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Registra un nuevo producto en el sistema.

    ### Parámetros obligatorios:
    - **codigo**: SKU o código único del producto
    - **nombre**: Nombre del producto
    - **precio_unitario**: Precio de venta

    ### Ejemplo de JSON:
    ```json
    {
        "codigo": "PROD-001",
        "nombre": "Laptop Dell Inspiron 15",
        "descripcion": "Laptop para uso empresarial",
        "tipo": "producto",
        "categoria": "Tecnología",
        "marca": "Dell",
        "precio_unitario": 2500.00,
        "costo_unitario": 2000.00,
        "aplica_igv": true,
        "igv_porcentaje": 1800,
        "tipo_afectacion_igv": "10",
        "moneda": "PEN",
        "unidad_medida": "UND",
        "tiene_stock": true,
        "cantidad_stock": 10,
        "estado": "activo"
    }
    ```
    """
    producto = await crear_producto(db, data)
    return producto


@router.get(
    "/listar",
    response_model=list[ProductoResponse],
    summary="Listar productos"
)
async def listar(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(1000, ge=1, le=5000, description="Máximo de registros"),
    estado: Optional[str] = Query(None, description="Filtrar por estado: activo | inactivo"),
    busqueda: Optional[str] = Query(None, description="Buscar por razón social, RUC o nombre comercial"),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    productos = await listar_productos(db, skip, limit, estado, busqueda)
    return productos


@router.put(
    "/actualizar/{id}",
    response_model=ProductoResponse,
    summary="Actualizar producto"
)
async def actualizar(
    id: int,
    data: ProductoRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Actualiza un producto existente por su ID."""
    producto = await actualizar_producto(db, id, data)
    return producto


@router.delete(
    "/eliminar/{id}",
    response_model=ProductoResponse,
    summary="Eliminar producto"
)
async def eliminar(
    id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Elimina un producto existente (soft delete)"""
    producto = await eliminar_producto(db, id)
    return producto

