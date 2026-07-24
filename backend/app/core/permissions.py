# backend/app/core/permissions.py

from enum import Enum
from typing import List
from fastapi import HTTPException, Depends
from app.core.security import get_current_user

class Permiso(Enum):
    """Enum de permisos"""
    CREAR_FACTURA = "facturas:crear"
    LEER_FACTURA = "facturas:leer"
    EDITAR_FACTURA = "facturas:editar"
    ENVIAR_SUNAT = "facturas:enviar_sunat"
    CREAR_COTIZACION = "cotizaciones:crear"
    # ... etc

async def verificar_permiso(permiso: str):
    """Dependency para verificar permisos"""
    async def check_permission(current_user = Depends(get_current_user)):
        rol = current_user["rol"]
        permisos = PERMISOS_POR_ROL.get(rol, [])
        
        if permiso not in permisos and "admin:*" not in permisos:
            raise HTTPException(
                status_code=403,
                detail=f"No tienes permiso para: {permiso}"
            )
        
        return current_user
    
    return check_permission

# Uso en rutas
@app.post("/api/facturas")
async def crear_factura(
    factura_data: dict,
    current_user = Depends(verificar_permiso("facturas:crear"))
):
    # Solo usuarios con permiso "facturas:crear" llegan aquí
    pass