from app.core.dependencies import CurrentUser, get_current_user, get_tenant_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.productos import ProductoRequest, ProductoResponse
from app.services.producto_service import crear_producto

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