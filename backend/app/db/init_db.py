# backend/app/db/init_db.py

"""
Script para crear toda la arquitectura de BD en PostgreSQL.

Uso:
python -c "from app.db.init_db import crear_bd_completa; crear_bd_completa()"

"""

from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import logging

from app.core.config import settings
from app.models import Base

logger = logging.getLogger(__name__)

def crear_bd_completa():
    """
    Crea toda la arquitectura de BD:
    1. Schema public con tablas compartidas
    2. Schema empresa_1 como ejemplo
    3. Todos los índices y constraints
    """

    db_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    print(f"\n🔍 DEBUG: Conectando a: {db_url}")
    print(f"🔍 DEBUG: db_name = {settings.db_name}")
    print(f"🔍 DEBUG: db_host = {settings.db_host}")
    print(f"🔍 DEBUG: db_port = {settings.db_port}\n")
    engine = create_engine(db_url, poolclass=NullPool, echo=False)
    
    try:
        with engine.connect() as connection:
            
            # ===== 1. CREAR SCHEMA PUBLIC =====
            logger.info("Creando schema public...")
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS public"))
            
            # ===== 2. CREAR TABLAS EN SCHEMA PUBLIC =====
            logger.info("Creando tablas en schema public...")
            
            # Tabla: empresas
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS public.empresas (
                    id SERIAL PRIMARY KEY,
                    ruc VARCHAR(11) NOT NULL UNIQUE,
                    razon_social VARCHAR(255) NOT NULL,
                    nombre_comercial VARCHAR(255),
                    db_schema VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(255),
                    telefono VARCHAR(20),
                    direccion VARCHAR(500),
                    ubigeo VARCHAR(6),
                    certificado_digital_path VARCHAR(500),
                    certificado_password_hash VARCHAR(255),
                    certificado_expiracion TIMESTAMP,
                    ambiente_sunat VARCHAR(20) DEFAULT 'beta',
                    usuario_sol VARCHAR(50),
                    moneda_base VARCHAR(3) DEFAULT 'PEN',
                    aplicar_igv_defecto BOOLEAN DEFAULT TRUE,
                    igv_porcentaje NUMERIC(10, 2) DEFAULT 18.00,
                    direccion_fiscal VARCHAR(500),
                    ubigeo_fiscal VARCHAR(6),
                    numero_establecimiento INTEGER DEFAULT 0,
                    plan_id INTEGER,
                    estado VARCHAR(20) DEFAULT 'activa',
                    deleted_at TIMESTAMP,
                    logo_url VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """))
            
            # Índices para empresas
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_empresas_ruc ON public.empresas(ruc)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_empresas_db_schema ON public.empresas(db_schema)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_empresas_estado ON public.empresas(estado)"))
            
            # Tabla: usuarios
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS public.usuarios (
                    id SERIAL PRIMARY KEY,
                    empresa_id INTEGER NOT NULL REFERENCES public.empresas(id),
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    nombre VARCHAR(255) NOT NULL,
                    apellido VARCHAR(255),
                    rol VARCHAR(50) DEFAULT 'vendedor',
                    estado VARCHAR(20) DEFAULT 'activo',
                    deleted_at TIMESTAMP,
                    two_factor_enabled BOOLEAN DEFAULT FALSE,
                    two_factor_secret VARCHAR(32),
                    ultimo_login TIMESTAMP,
                    ip_ultimo_login VARCHAR(45),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """))
            
            # Índices para usuarios
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_usuarios_email ON public.usuarios(email)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_usuarios_empresa_id ON public.usuarios(empresa_id)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_usuarios_estado ON public.usuarios(estado)"))
            
            # Tabla: audit_global
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS public.audit_global (
                    id SERIAL PRIMARY KEY,
                    empresa_id INTEGER NOT NULL REFERENCES public.empresas(id),
                    usuario_id INTEGER NOT NULL REFERENCES public.usuarios(id),
                    accion VARCHAR(100) NOT NULL,
                    tabla VARCHAR(100) NOT NULL,
                    registro_id INTEGER,
                    cambios VARCHAR(2000),
                    descripcion VARCHAR(500),
                    ip_usuario VARCHAR(45),
                    user_agent VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """))
            
            # Índices para audit_global
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_global_empresa_timestamp ON public.audit_global(empresa_id, created_at)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_global_usuario_timestamp ON public.audit_global(usuario_id, created_at)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_global_accion ON public.audit_global(accion)"))

            # Tabla: configuracion_empresa
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS public.configuracion_empresa (
                    id SERIAL PRIMARY KEY,
                    empresa_id INTEGER NOT NULL UNIQUE REFERENCES public.empresas(id) ON DELETE CASCADE,
                    
                    serie_factura VARCHAR(4) DEFAULT 'F001',
                    serie_boleta VARCHAR(4) DEFAULT 'B001',
                    serie_nc VARCHAR(4) DEFAULT 'NC01',
                    serie_nd VARCHAR(4) DEFAULT 'ND01',
                    
                    ruta_certificado VARCHAR(500),
                    contraseña_certificado VARCHAR(255),
                    
                    logo_url VARCHAR(500),
                    telefono VARCHAR(20),
                    email VARCHAR(255),
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """))
            
            # Índices para configuracion_empresa
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_configuracion_empresa_empresa_id ON public.configuracion_empresa(empresa_id)"))

           
            # Tabla: password_reset_tokens
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS public.password_reset_tokens (
                    id SERIAL PRIMARY KEY,
                    
                    usuario_id INTEGER NOT NULL REFERENCES public.usuarios(id) ON DELETE CASCADE,
                    
                    token VARCHAR(64) NOT NULL UNIQUE,
                    
                    expires_at TIMESTAMP NOT NULL,
                    
                    used_at TIMESTAMP,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """))
            
            # Índices para password_reset_tokens
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_reset_token ON public.password_reset_tokens(token)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_reset_usuario ON public.password_reset_tokens(usuario_id)"))
            
            # ===== 3. CREAR SCHEMA EMPRESA_1 (EJEMPLO) =====
            logger.info("Creando schema empresa_1...")
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS empresa_1"))
            
            # ===== 4. CREAR TABLAS EN SCHEMA EMPRESA_1 =====
            logger.info("Creando tablas en schema empresa_1...")
            
            # Tabla: productos
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS empresa_1.productos (
                    id SERIAL PRIMARY KEY,
                    codigo VARCHAR(100) NOT NULL UNIQUE,
                    nombre VARCHAR(255) NOT NULL,
                    descripcion VARCHAR(1000),
                    codigo_unspsc VARCHAR(8),
                    tipo VARCHAR(50) DEFAULT 'producto',
                    categoria VARCHAR(100),
                    marca VARCHAR(100),
                    precio_unitario NUMERIC(12,4) NOT NULL,
                    costo_unitario NUMERIC(12,4),
                    precio_distribuidor NUMERIC(12,4),
                    aplica_igv BOOLEAN DEFAULT TRUE,
                    igv_porcentaje NUMERIC(10, 2) DEFAULT 18.00,
                    tipo_afectacion_igv VARCHAR(2) DEFAULT '10',
                    moneda VARCHAR(3) DEFAULT 'PEN',
                    unidad_medida VARCHAR(20) DEFAULT 'UND',
                    tiene_stock BOOLEAN DEFAULT FALSE,
                    cantidad_stock INTEGER DEFAULT 0,
                    estado VARCHAR(20) DEFAULT 'activo',
                    deleted_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """))
            
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_productos_codigo ON empresa_1.productos(codigo)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_productos_estado ON empresa_1.productos(estado)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_productos_categoria ON empresa_1.productos(categoria)"))
            
            # Tabla: clientes
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS empresa_1.clientes (
                    id SERIAL PRIMARY KEY,
                    tipo_documento VARCHAR(10) NOT NULL,
                    numero_documento VARCHAR(15) NOT NULL UNIQUE,
                    razon_social VARCHAR(255) NOT NULL,
                    nombre_comercial VARCHAR(255),
                    email VARCHAR(255),
                    telefono VARCHAR(20),
                    direccion_completa VARCHAR(500),
                    ubigeo VARCHAR(6),
                    es_cliente_frecuente BOOLEAN DEFAULT FALSE,
                    estado VARCHAR(20) DEFAULT 'activo',
                    deleted_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """))
            
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_clientes_numero_documento ON empresa_1.clientes(numero_documento)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_clientes_razon_social ON empresa_1.clientes(razon_social)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_clientes_estado ON empresa_1.clientes(estado)"))
            
            # Tabla: cotizaciones
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS empresa_1.cotizaciones (
                    id SERIAL PRIMARY KEY,
                    numero_cotizacion VARCHAR(50) NOT NULL UNIQUE,
                    cliente_id INTEGER NOT NULL REFERENCES empresa_1.clientes(id),
                    usuario_id INTEGER NOT NULL REFERENCES public.usuarios(id),
                    subtotal NUMERIC(12,4) NOT NULL,
                    descuento_total NUMERIC(12,4) DEFAULT 0,
                    igv_total NUMERIC(12,4) DEFAULT 0,
                    total NUMERIC(12,4) NOT NULL,
                    moneda VARCHAR(3) DEFAULT 'PEN',
                    tipo_cambio NUMERIC(10, 6),
                    estado VARCHAR(50) DEFAULT 'borrador',
                    vigencia_dias INTEGER DEFAULT 30,
                    fecha_vencimiento DATE,
                    convertida_a_factura_id INTEGER,
                    notas_internas VARCHAR(1000),
                    terminos_condiciones VARCHAR(2000),
                    deleted_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """))
            
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_cotizaciones_numero ON empresa_1.cotizaciones(numero_cotizacion)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_cotizaciones_cliente_id ON empresa_1.cotizaciones(cliente_id)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_cotizaciones_estado ON empresa_1.cotizaciones(estado)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_cotizaciones_fecha_creacion ON empresa_1.cotizaciones(created_at)"))
            
            # Tabla: items_cotizacion
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS empresa_1.items_cotizacion (
                    id SERIAL PRIMARY KEY,
                    cotizacion_id INTEGER NOT NULL REFERENCES empresa_1.cotizaciones(id) ON DELETE CASCADE,
                    producto_id INTEGER NOT NULL REFERENCES empresa_1.productos(id),
                    cantidad NUMERIC(12,4) NOT NULL,
                    precio_unitario NUMERIC(12,4) NOT NULL,
                    igv_porcentaje NUMERIC(10, 2) DEFAULT 18.00,
                    igv_monto NUMERIC(12,4),
                    subtotal NUMERIC(12,4) NOT NULL,
                    total NUMERIC(12,4) NOT NULL,
                    orden_item INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    UNIQUE(cotizacion_id, producto_id)
                )
            """))
            
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_items_cot_cotizacion_id ON empresa_1.items_cotizacion(cotizacion_id)"))
            
            # Tabla: facturas (LA MÁS IMPORTANTE)
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS empresa_1.facturas (
                    id SERIAL PRIMARY KEY,
                    numero_serie VARCHAR(4) NOT NULL,
                    numero_comprobante VARCHAR(8) NOT NULL,
                    cliente_id INTEGER NOT NULL REFERENCES empresa_1.clientes(id),
                    usuario_id INTEGER NOT NULL REFERENCES public.usuarios(id),
                    cotizacion_id INTEGER REFERENCES empresa_1.cotizaciones(id),
                    tipo_comprobante VARCHAR(2) DEFAULT '01',
                    tipo_operacion VARCHAR(4) DEFAULT '0101',
                    moneda VARCHAR(3) DEFAULT 'PEN',
                    tipo_cambio NUMERIC(10, 6),
                    subtotal NUMERIC(12,4) NOT NULL,
                    descuento_total NUMERIC(12,4) DEFAULT 0,
                    igv_total NUMERIC(12,4) NOT NULL,
                    total NUMERIC(12,4) NOT NULL,
                    subtotal_en_pen NUMERIC(12, 4) NULL,
                    total_en_pen NUMERIC(12, 4) NULL,
                    fecha_emision DATE NOT NULL,
                    hora_emision TIME NOT NULL,
                    fecha_vencimiento DATE,
                    forma_pago VARCHAR(50) DEFAULT 'Contado',
                    detalle_credito JSON,
                    ubigeo_origen VARCHAR(6),
                    ubigeo_destino VARCHAR(6),
                    estado VARCHAR(50) DEFAULT 'borrador',
                    xml_generado TEXT,
                    xml_firmado BYTEA,
                    codigo_hash VARCHAR(100),
                    numero_cdr VARCHAR(50),
                    estado_sunat VARCHAR(50),
                    respuesta_sunat JSON,
                    intentos_sunat INTEGER DEFAULT 0,
                    ultimo_intento_sunat TIMESTAMP,
                    proximo_intento_sunat TIMESTAMP,
                    pdf_url VARCHAR(500),
                    deleted_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    UNIQUE(numero_serie, numero_comprobante)
                )
            """))
            
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_facturas_numero_serie ON empresa_1.facturas(numero_serie)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_facturas_numero_comprobante ON empresa_1.facturas(numero_comprobante)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_facturas_cliente_id ON empresa_1.facturas(cliente_id)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_facturas_estado ON empresa_1.facturas(estado)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_facturas_estado_sunat ON empresa_1.facturas(estado_sunat)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_facturas_fecha_emision ON empresa_1.facturas(fecha_emision)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_facturas_created_at ON empresa_1.facturas(created_at)"))
            
            # Tabla: items_factura
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS empresa_1.items_factura (
                    id SERIAL PRIMARY KEY,
                    factura_id INTEGER NOT NULL REFERENCES empresa_1.facturas(id) ON DELETE CASCADE,
                    producto_id INTEGER NOT NULL REFERENCES empresa_1.productos(id),
                    cantidad NUMERIC(12,4) NOT NULL,
                    precio_unitario NUMERIC(12,4) NOT NULL,
                    moneda_original VARCHAR(3),
                    precio_original NUMERIC(12, 4),
                    tipo_cambio_usado NUMERIC(10, 6),
                    precio_en_factura NUMERIC(12, 4),
                    tipo_afectacion_igv VARCHAR(2) DEFAULT '10',
                    igv_porcentaje NUMERIC(10, 2) DEFAULT 18.00,
                    igv_monto NUMERIC(12,4),
                    codigo_producto_sunat VARCHAR(8),
                    subtotal NUMERIC(12,4) NOT NULL,
                    total NUMERIC(12,4) NOT NULL,
                    orden_item INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    UNIQUE(factura_id, producto_id)
                )
            """))
            
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_items_fact_factura_id ON empresa_1.items_factura(factura_id)"))
            
            # Tabla: secuencias (CRÍTICA)
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS empresa_1.secuencias (
                    id SERIAL PRIMARY KEY,
                    tipo_documento VARCHAR(2) NOT NULL,
                    serie VARCHAR(4) NOT NULL,
                    proximo_numero INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    UNIQUE(tipo_documento, serie)
                )
            """))
            
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_secuencias_tipo_documento ON empresa_1.secuencias(tipo_documento)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_secuencias_serie ON empresa_1.secuencias(serie)"))
            
            # Inicializar secuencias
            connection.execute(text("""
                INSERT INTO empresa_1.secuencias (tipo_documento, serie, proximo_numero)
                VALUES 
                ('01', 'F001', 1), 
                ('01', 'F002', 1),
                ('03', 'B001', 1), 
                ('03', 'B002', 1),
                ('07', 'NC01', 1),
                ('08', 'ND01', 1)
                ON CONFLICT (tipo_documento, serie) DO NOTHING
            """))
            
            # Tabla: notas_comprobante
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS empresa_1.notas_comprobante (
                    id SERIAL PRIMARY KEY,
                    tipo VARCHAR(20) NOT NULL,
                    numero_serie VARCHAR(4) NOT NULL,
                    numero_comprobante VARCHAR(8) NOT NULL,
                    tipo_operacion VARCHAR(4) DEFAULT '0101',
                    factura_referenciada_id INTEGER NOT NULL REFERENCES empresa_1.facturas(id),
                    usuario_id INTEGER NOT NULL REFERENCES public.usuarios(id),
                    motivo VARCHAR(2) NOT NULL,
                    descripcion VARCHAR(500),
                    monto NUMERIC(12,4) NOT NULL,
                    estado VARCHAR(50) DEFAULT 'borrador',
                    xml_generado TEXT,
                    xml_firmado BYTEA,
                    codigo_hash VARCHAR(100),
                    numero_cdr VARCHAR(50),
                    estado_sunat VARCHAR(50),
                    respuesta_sunat JSON,
                    intentos_sunat INTEGER DEFAULT 0,
                    ultimo_intento_sunat TIMESTAMP,
                    proximo_intento_sunat TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    UNIQUE(tipo, numero_serie, numero_comprobante)
                )
            """))
            
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_notas_tipo ON empresa_1.notas_comprobante(tipo)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_notas_factura_id ON empresa_1.notas_comprobante(factura_referenciada_id)"))
            
            # Tabla: audit_logs
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS empresa_1.audit_logs (
                    id BIGSERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL REFERENCES public.usuarios(id),
                    accion VARCHAR(100) NOT NULL,
                    tabla VARCHAR(100) NOT NULL,
                    registro_id INTEGER,
                    cambios VARCHAR(2000),
                    descripcion VARCHAR(500),
                    ip_usuario VARCHAR(45),
                    user_agent VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """))
            
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_usuario_id ON empresa_1.audit_logs(usuario_id)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON empresa_1.audit_logs(created_at)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_accion ON empresa_1.audit_logs(accion)"))
            
            # Commit
            connection.commit()
            
            logger.info("✅ BD creada completamente en PostgreSQL")
            
            # Resumen
            print("\n" + "="*60)
            print("ARQUITECTURA DE BD CREADA EXITOSAMENTE")
            print("="*60)
            print("\nSchema Public (Compartido):")
            print("  ├─ empresas")
            print("  ├─ usuarios")
            print("  └─ audit_global")
            print("\nSchema empresa_1 (Ejemplo de Tenant):")
            print("  ├─ productos")
            print("  ├─ clientes")
            print("  ├─ cotizaciones")
            print("  ├─ items_cotizacion")
            print("  ├─ facturas")
            print("  ├─ items_factura")
            print("  ├─ secuencias")
            print("  ├─ notas_comprobante")
            print("  └─ audit_logs")
            print("\nPróximos pasos:")
            print("  1. Insertar empresa en public.empresas")
            print("  2. Insertar usuario en public.usuarios")
            print("  3. Usar el sistema")
            print("="*60 + "\n")
    
    except Exception as e:
        logger.error(f"Error creando BD: {e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    crear_bd_completa()