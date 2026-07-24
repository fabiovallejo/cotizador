from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging 
import os

from app.core.config import settings 

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicación")
    yield
    logger.info("Apagando aplicación")

app = FastAPI(
    title = "API Cotizaciones",
    description = "Sistema de cotizaciones para Perú",
    version = "1.0.0",
    lifespan = lifespan
)

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000", "http://localhost:8000"],
    allow_credentials = True,
    allow_methods =["*"],
    allow_headers = ["*"],
)

#Health Check
@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.environment}

# Archivos estáticos (logos, etc.)
os.makedirs("uploads/logos", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

#Rutas
from app.api.auth.routes import router as auth_router
from app.api.admin.routes import router as admin_router
from app.api.clientes.routes import router as clientes_router
from app.api.productos.routes import router as productos_router
from app.api.facturas.routes import router as facturas_router
from app.api.cotizaciones.routes import router as cotizaciones_router
from app.api.empresa.routes import router as empresa_router
from app.api.utils.routes import router as utils_router
from app.api.config.routes import router as config_router
from app.api.reportes.routes import router as reportes_router
from app.api.importacion.routes import router as importacion_router
from app.api.chat.routes import router as chat_router

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(clientes_router)
app.include_router(productos_router)
app.include_router(facturas_router)
app.include_router(cotizaciones_router)
app.include_router(empresa_router)
app.include_router(utils_router)
app.include_router(config_router)
app.include_router(reportes_router)
app.include_router(importacion_router)
app.include_router(chat_router)

logger.info(f" Aplicación configurada en modo {settings.environment}")

