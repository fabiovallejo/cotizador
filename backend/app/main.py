from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging 

from app.core.config import settings 

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicación")
    yield
    logger.info("Apagando aplicación")

app = FastAPI(
    title = "API Facturación SUNAT",
    description = "Sistema de facturación electrónica para Perú",
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

#Rutas
from app.api.auth.routes import router as auth_router
from app.api.admin.routes import router as admin_router
from app.api.clientes.routes import router as clientes_router
from app.api.productos.routes import router as productos_router
from app.api.facturas.routes import router as facturas_router
from app.api.cotizaciones.routes import router as cotizaciones_router

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(clientes_router)
app.include_router(productos_router)
app.include_router(facturas_router)
app.include_router(cotizaciones_router)

logger.info(f" Aplicación configurada en modo {settings.environment}")

