from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging 

from app.core.config import settings 
from app.db.tenant_manager import TenantManager

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

tenant_manager = TenantManager(settings.database_url)

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
from app.routes import auth, clientes, productos 

logger.info(f" Aplicación configurada en modo {settings.environment}")
