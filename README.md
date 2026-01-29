# 🧾 Sistema de Facturación Electrónica Multi-Tenant para Perú

**Versión:** 1.0.0 (En Desarrollo)  
**Última Actualización:** Enero 2025  
**Estado:** MVP Phase

---

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Objetivos del Proyecto](#objetivos-del-proyecto)
3. [Arquitectura](#arquitectura)
4. [Stack Tecnológico](#stack-tecnológico)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Guía de Instalación](#guía-de-instalación)
7. [Guía de Desarrollo](#guía-de-desarrollo)
8. [Flujos Principales](#flujos-principales)
9. [Especificaciones Técnicas](#especificaciones-técnicas)
10. [Roadmap](#roadmap)
11. [Configuración de Entorno](#configuración-de-entorno)
12. [Deployment](#deployment)
13. [Contribución](#contribución)

---

## 📌 Descripción General

**Facturación SUNAT** es un sistema SaaS de **facturación electrónica multi-tenant** diseñado específicamente para empresas peruanas que requieren cumplimiento normativo con la SUNAT (Superintendencia Nacional de Aduanas y de Administración Tributaria).

### Características Principales

- ✅ **Multi-tenant con aislamiento total**: Cada cliente tiene su propio schema en PostgreSQL
- ✅ **Integración directa con SUNAT**: Firma digital y envío automático de facturas
- ✅ **Cotizaciones integradas**: Convertibles directamente a facturas
- ✅ **Gestión de productos y clientes**: Catálogo y registro de clientes por empresa
- ✅ **Notas de crédito/débito**: Comprobantes adicionales según normativa
- ✅ **Backups por cliente**: Seguridad y cumplimiento GDPR/normativa local
- ✅ **Reintentos automáticos**: Si SUNAT falla, el sistema reintenta
- ✅ **Dashboard en tiempo real**: Monitoreo de estado de facturas
- ✅ **API REST completa**: Para integraciones de terceros

### ¿A Quién Va Dirigido?

- Pequeños negocios (tiendas, restaurantes, consultorías)
- Medianas empresas (constructoras, agencias, distribuidoras)
- Cualquier empresa en Perú que deba facturar electrónicamente

---

## 🎯 Objetivos del Proyecto

### Objetivos Primarios

1. **Cumplimiento SUNAT**
   - Generar facturas válidas según estándares UBL 2.1
   - Firma digital automática con certificados X.509
   - Envío confiable a servidores de SUNAT
   - Almacenamiento de comprobantes de recepción (CDR)

2. **Facilidad de Uso**
   - Interfaz intuitiva sin requerer conocimiento técnico
   - Proceso de facturación en menos de 3 clics
   - Visualización clara del estado de trámite

3. **Seguridad y Confiabilidad**
   - Aislamiento total de datos entre clientes
   - Encriptación de información sensible
   - Auditoría completa de operaciones
   - Backups automáticos por cliente

4. **Escalabilidad**
   - Soportar miles de clientes simultáneamente
   - Manejo de millones de facturas
   - Arquitectura preparada para crecer

5. **Integración**
   - API REST para integración con otros sistemas
   - Webhooks para eventos
   - Exportación de datos en múltiples formatos

### Objetivos Secundarios

- Reducir carga operativa de contabilidad
- Automatizar reconciliación fiscal
- Proporcionar reportes contables
- Mejorar flujo de caja con informes

---

## 🏗️ Arquitectura

### Enfoque Multi-Tenant (Schema-per-Tenant)

```
PostgreSQL - Una BD única, múltiples schemas aislados

├─ Schema: public (COMPARTIDO)
│  ├─ Tabla: empresas
│  │  └─ Contiene: RUC, razón social, schema asignado, certificado
│  │
│  └─ Tabla: usuarios
│     └─ Contiene: email, contraseña, rol, empresa_id (FK)
│
├─ Schema: empresa_1 (AISLADO)
│  ├─ productos
│  ├─ clientes
│  ├─ cotizaciones
│  ├─ items_cotizacion
│  ├─ facturas
│  ├─ items_factura
│  ├─ secuencias (para numeración)
│  ├─ notas_comprobante
│  └─ audit_logs
│
├─ Schema: empresa_2 (AISLADO)
│  └─ (misma estructura que empresa_1)
│
└─ Schema: empresa_N (AISLADO)
   └─ ...
```

### ¿Por qué Schema-per-Tenant?

| Criterio | Row-Level | **Schema-per-Tenant** | DB-per-Tenant |
|----------|-----------|----------------------|---------------|
| Aislamiento | ⚠️ En código | ✅ En BD | ✅ En BD |
| Costo | $ | $$ | $$$$ |
| Backup | Tedioso | ✅ Trivial | ✅ Trivial |
| Escalabilidad | < 100 | < 10k | < 10k |
| Complejidad | Baja | **Media** | Alta |

### Flujo de Datos (Alto Nivel)

```
Navegador (Frontend)
    ↓ HTTPS
Frontend Next.js (3000)
    ↓
CORS allowed (localhost:8000)
    ↓
FastAPI Backend (8000)
    ├─ JWT validation
    ├─ Extrae empresa_id del token
    ├─ Set search_path en PostgreSQL al schema correcto
    ├─ Query en schema de empresa específica
    └─ ✅ Devuelve datos isolados
    
Backend encola tasks Celery para:
    ├─ Firma digital de facturas
    ├─ Envío a SUNAT
    └─ Reintentos automáticos (Redis + Celery Beat)
```

### Flujo de Facturación (Detallado)

```
1. Usuario crea factura en frontend
   POST /api/facturas
   {cliente_id, items, total}
   
   ↓
   
2. FastAPI valida y crea registro
   - Estado: "borrador"
   - Encola task Celery: "firmar_y_enviar_sunat"
   - Devuelve inmediatamente: {factura_id, estado}
   
   ↓
   
3. Celery Worker (en background)
   ├─ Obtiene factura de BD
   ├─ Genera XML en formato UBL 2.1 (estándar SUNAT)
   ├─ Carga certificado digital de empresa
   ├─ Firma XML criptográficamente
   ├─ Conecta a servidor SUNAT vía WebService SOAP
   ├─ Recibe respuesta:
   │  ├─ ACEPTADA: estado_sunat="aceptada", número_cdr guardado
   │  ├─ RECHAZADA: estado_sunat="rechazada", errores registrados
   │  └─ ERROR CONEXIÓN: reintenta en 30 min (exponential backoff)
   └─ Actualiza BD con respuesta
   
   ↓
   
4. Usuario puede consultar estado
   GET /api/facturas/{id}/estado-sunat
   ← {estado_sunat: "aceptada", numero_cdr: "..."}
   
   ↓
   
5. Generar PDF con comprobante
   GET /api/facturas/{id}/pdf
   ← PDF descargable con sello SUNAT
```

---

## 🛠️ Stack Tecnológico

### Backend

```
Python 3.11+
├─ FastAPI 0.104.1 (Framework web async)
│  └─ Validación automática con Pydantic
│  └─ Documentación OpenAPI auto-generada
│
├─ SQLAlchemy 2.0.23 (ORM)
│  └─ Manejo multi-tenant con search_path
│  └─ Type hints completos
│
├─ PostgreSQL 16 (Base de datos)
│  └─ Schema-per-tenant
│  └─ JSONB para respuestas SUNAT
│  └─ Índices optimizados
│
├─ Celery 5.3.4 (Task queue distribuida)
│  └─ Firma digital de facturas
│  └─ Envío a SUNAT
│  └─ Reintentos con backoff exponencial
│
├─ Redis 7 (Cache + Broker)
│  └─ Broker para Celery
│  └─ Cache de sesiones
│  └─ Rate limiting
│
├─ Cryptography 41.0.7 (Firma digital)
│  └─ Manejo de certificados X.509
│  └─ Firma XAdES SUNAT
│
├─ Zeep 4.2.1 (SOAP client)
│  └─ Conexión con WebService SUNAT
│
└─ ReportLab 4.0.7 (Generación de PDFs)
   └─ PDFs de facturas
   └─ Plantillas personalizables
```

### Frontend

```
Node.js 20+
├─ Next.js 15 (Framework React)
│  └─ App Router (última arquitectura)
│  └─ Server Components
│  └─ TypeScript nativo
│
├─ React 19 (UI Library)
│  └─ Hooks custom para multi-tenant
│  └─ Context API para estado global
│
├─ TypeScript 5.3 (Type Safety)
│  └─ Types para toda la aplicación
│
├─ Tailwind CSS (Styling)
│  └─ Utilities-first
│  └─ Responsive design
│
├─ Axios (HTTP Client)
│  └─ Interceptores para auth
│  └─ Error handling
│
├─ Zustand (State Management)
│  └─ Alternativa a Redux (más simple)
│
├─ React Hook Form (Formularios)
│  └─ Validación con Zod
│  └─ Sin re-renders innecesarios
│
└─ Shadcn/ui (Componentes UI)
   └─ Tabla de productos
   └─ Diálogos
   └─ Formularios
```

### DevOps & Infrastructure

```
Docker 24+
├─ Contenedores para todos los servicios
├─ Docker Compose para desarrollo
└─ Orquestación en producción

Git / GitHub
├─ Control de versiones
├─ CI/CD (GitHub Actions)
└─ Code review

Deployment
├─ Backend: DigitalOcean / AWS / Railway
├─ Frontend: Vercel (recomendado para Next.js)
├─ Database: AWS RDS / DigitalOcean Managed
└─ Redis: DigitalOcean / AWS ElastiCache
```

---

## 📁 Estructura del Proyecto

```
facturacion-saas/
│
├─ 📂 backend/
│  ├─ 📂 app/
│  │  ├─ 📂 core/
│  │  │  ├─ config.py           # Variables de entorno
│  │  │  ├─ database.py         # Conexión PostgreSQL
│  │  │  ├─ security.py         # JWT, hashing de passwords
│  │  │  └─ middleware.py       # Tenant middleware
│  │  │
│  │  ├─ 📂 models/
│  │  │  ├─ shared.py           # Modelos públicos (Empresa, Usuario)
│  │  │  └─ tenant.py           # Modelos por tenant (Producto, Cliente, etc)
│  │  │
│  │  ├─ 📂 schemas/
│  │  │  ├─ cliente_schema.py    # Pydantic schemas (validación)
│  │  │  ├─ producto_schema.py
│  │  │  ├─ cotizacion_schema.py
│  │  │  ├─ factura_schema.py
│  │  │  └─ sunat_schema.py
│  │  │
│  │  ├─ 📂 repositories/
│  │  │  ├─ base_repository.py   # Base class con multi-tenant
│  │  │  ├─ cliente_repository.py
│  │  │  ├─ producto_repository.py
│  │  │  ├─ cotizacion_repository.py
│  │  │  └─ factura_repository.py
│  │  │
│  │  ├─ 📂 services/
│  │  │  ├─ cliente_service.py   # Lógica de negocio
│  │  │  ├─ producto_service.py
│  │  │  ├─ cotizacion_service.py
│  │  │  ├─ factura_service.py
│  │  │  ├─ sunat_service.py     # 🔴 CRÍTICO: Firma digital + envío
│  │  │  ├─ signature_service.py # Manejo de certificados
│  │  │  └─ pdf_service.py       # Generación de PDFs
│  │  │
│  │  ├─ 📂 routes/
│  │  │  ├─ auth.py              # POST /auth/login, /auth/register
│  │  │  ├─ clientes.py          # CRUD de clientes
│  │  │  ├─ productos.py         # CRUD de productos
│  │  │  ├─ cotizaciones.py      # CRUD de cotizaciones
│  │  │  ├─ facturas.py          # CRUD de facturas + envío SUNAT
│  │  │  ├─ empresas.py          # Gestión de empresas
│  │  │  └─ health.py            # Health check
│  │  │
│  │  ├─ 📂 tasks/
│  │  │  ├─ __init__.py          # Configuración de Celery
│  │  │  ├─ factura_tasks.py     # 🔴 CRÍTICO: Tasks de SUNAT
│  │  │  └─ backup_tasks.py      # Tareas de backup
│  │  │
│  │  ├─ 📂 db/
│  │  │  ├─ tenant_manager.py    # Creación de schemas
│  │  │  ├─ init.sql             # Script inicial de BD
│  │  │  └─ migrations/          # Alembic migrations
│  │  │
│  │  ├─ 📂 utils/
│  │  │  ├─ logger.py            # Logging
│  │  │  ├─ validators.py        # Validadores custom
│  │  │  ├─ sunat_constants.py   # Códigos SUNAT
│  │  │  └─ helpers.py           # Funciones útiles
│  │  │
│  │  ├─ main.py                 # Punto de entrada FastAPI
│  │  └─ __init__.py
│  │
│  ├─ 📂 tests/
│  │  ├─ test_auth.py            # Tests de autenticación
│  │  ├─ test_clientes.py        # Tests de clientes
│  │  ├─ test_facturas.py        # Tests de facturas
│  │  └─ test_sunat.py           # Tests de integración SUNAT
│  │
│  ├─ requirements.txt            # Dependencias Python
│  ├─ .env                        # Variables de entorno (git ignored)
│  ├─ Dockerfile                  # Imagen Docker
│  ├─ docker-entrypoint.sh        # Script de inicio
│  └─ README.md                   # Documentación backend
│
│
├─ 📂 frontend/
│  ├─ 📂 app/
│  │  ├─ layout.tsx               # Layout global
│  │  ├─ page.tsx                 # Home page
│  │  │
│  │  ├─ 📂 auth/
│  │  │  ├─ login/
│  │  │  │  └─ page.tsx           # Página de login
│  │  │  └─ register/
│  │  │     └─ page.tsx           # Página de registro
│  │  │
│  │  ├─ 📂 dashboard/
│  │  │  ├─ page.tsx              # Dashboard general
│  │  │  ├─ layout.tsx
│  │  │  │
│  │  │  └─ 📂 [empresa_id]/
│  │  │     ├─ page.tsx           # Dashboard de empresa
│  │  │     │
│  │  │     ├─ 📂 productos/
│  │  │     │  ├─ page.tsx        # Lista de productos
│  │  │     │  ├─ new/page.tsx    # Crear producto
│  │  │     │  └─ [id]/page.tsx   # Editar producto
│  │  │     │
│  │  │     ├─ 📂 clientes/
│  │  │     │  ├─ page.tsx
│  │  │     │  ├─ new/page.tsx
│  │  │     │  └─ [id]/page.tsx
│  │  │     │
│  │  │     ├─ 📂 cotizaciones/
│  │  │     │  ├─ page.tsx
│  │  │     │  ├─ new/page.tsx
│  │  │     │  └─ [id]/page.tsx
│  │  │     │
│  │  │     └─ 📂 facturas/
│  │  │        ├─ page.tsx
│  │  │        ├─ new/page.tsx
│  │  │        └─ [id]/page.tsx
│  │  │
│  │  └─ 📂 api/ (No necesario, hay FastAPI)
│  │
│  ├─ 📂 components/
│  │  ├─ 📂 layout/
│  │  │  ├─ Header.tsx
│  │  │  ├─ Sidebar.tsx
│  │  │  └─ Footer.tsx
│  │  │
│  │  ├─ 📂 forms/
│  │  │  ├─ ClienteForm.tsx
│  │  │  ├─ ProductoForm.tsx
│  │  │  ├─ CotizacionForm.tsx
│  │  │  └─ FacturaForm.tsx
│  │  │
│  │  ├─ 📂 tables/
│  │  │  ├─ ClientesTable.tsx
│  │  │  ├─ ProductosTable.tsx
│  │  │  └─ FacturasTable.tsx
│  │  │
│  │  ├─ 📂 dialogs/
│  │  │  ├─ ConfirmDialog.tsx
│  │  │  └─ EstadoFacturaDialog.tsx
│  │  │
│  │  └─ 📂 ui/ (shadcn/ui components)
│  │
│  ├─ 📂 lib/
│  │  ├─ api.ts                   # Cliente HTTP (Axios)
│  │  ├─ store.ts                 # Zustand store global
│  │  ├─ constants.ts             # Constantes de la app
│  │  └─ utils.ts                 # Funciones de utilidad
│  │
│  ├─ 📂 hooks/
│  │  ├─ useAuth.ts               # Hook de autenticación
│  │  ├─ useFetch.ts              # Hook para fetch genérico
│  │  ├─ useTenant.ts             # Hook para obtener empresa_id
│  │  └─ useForm.ts               # Hook para formularios
│  │
│  ├─ 📂 types/
│  │  ├─ index.ts                 # Types globales
│  │  ├─ sunat.ts                 # Types de SUNAT
│  │  └─ api.ts                   # Types de API
│  │
│  ├─ 📂 context/
│  │  └─ AuthContext.tsx          # Context de autenticación
│  │
│  ├─ 📂 styles/
│  │  ├─ globals.css
│  │  └─ variables.css
│  │
│  ├─ 📂 public/
│  │  ├─ logo.png
│  │  └─ favicon.ico
│  │
│  ├─ package.json
│  ├─ tsconfig.json
│  ├─ next.config.js
│  ├─ tailwind.config.ts
│  ├─ .env.local (git ignored)
│  ├─ Dockerfile
│  └─ README.md
│
│
├─ 📂 docs/
│  ├─ ARQUITECTURA.md            # Detalles de arquitectura
│  ├─ API.md                     # Documentación de endpoints
│  ├─ SUNAT_INTEGRATION.md       # Guía de integración SUNAT
│  ├─ DATABASE.md                # Schema de BD
│  ├─ DEPLOYMENT.md              # Guía de deployment
│  └─ TROUBLESHOOTING.md         # Solución de problemas
│
├─ 📂 scripts/
│  ├─ setup.sh                   # Script de instalación inicial
│  ├─ test.sh                    # Ejecutar tests
│  ├─ migrate.sh                 # Ejecutar migraciones
│  └─ backup_db.sh               # Backup de BD
│
├─ docker-compose.yml            # Stack completo (Dev)
├─ docker-compose.prod.yml       # Stack para producción
├─ .env.example                  # Template de variables
├─ .gitignore                    # Git ignore
├─ README.md                     # Este archivo
└─ LICENSE                       # Licencia MIT
```

---

## 🚀 Guía de Instalación

### Requisitos Previos

- **Python:** 3.11 o superior
- **Node.js:** 20 o superior
- **PostgreSQL:** 16
- **Redis:** 7
- **Git:** Control de versiones

### Instalación Rápida (Con Docker)

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/facturacion-saas.git
cd facturacion-saas

# 2. Crear archivo de entorno
cp .env.example .env
# Editar .env con tus valores

# 3. Iniciar con Docker Compose
docker-compose up -d

# 4. Verificar que todo está running
docker-compose ps

# 5. Acceder
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - Docs API: http://localhost:8000/docs
# - Flower Celery: http://localhost:5555
```

### Instalación Manual (Desarrollo Local)

Ver [INSTALACIÓN_COMPLETA.md](./docs/INSTALACION_COMPLETA.md)

---

## 💻 Guía de Desarrollo

### Setup Inicial

```bash
# Backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Ejecutar en Desarrollo

**Terminal 1: Backend**
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload
```

**Terminal 2: Celery Worker**
```bash
cd backend
source venv/bin/activate
celery -A app.tasks worker --loglevel=info
```

**Terminal 3: Frontend**
```bash
cd frontend
npm run dev
```

### Comandos Útiles

```bash
# Tests
pytest backend/tests/

# Linting
black backend/
flake8 backend/
isort backend/

# Migraciones BD
alembic upgrade head
alembic downgrade -1

# Backup BD
pg_dump -U facturacion facturacion_db > backup.sql

# Crear nuevo schema para empresa
python3 << 'EOF'
from app.db.tenant_manager import TenantManager
tm = TenantManager("postgresql://...")
tm.crear_schema_empresa(empresa_id=5, schema_name="empresa_5")
EOF
```

### Convenciones de Código

**Backend (Python)**
- Usar `snake_case` para variables y funciones
- Usar `CamelCase` para clases
- Type hints en todas las funciones
- Docstrings en clase y funciones públicas

**Frontend (TypeScript)**
- Usar `PascalCase` para componentes
- Usar `camelCase` para variables y funciones
- Interfaces para props de componentes
- Comentarios en lógica compleja

---

## 🔄 Flujos Principales

### 1. Registro de Nueva Empresa

```
POST /api/empresas/register
{
  "ruc": "20123456789",
  "razon_social": "Mi Empresa S.A.C",
  "email_admin": "admin@empresa.com",
  "password": "SecurePassword123!"
}

↓

Backend:
├─ Valida RUC (formato Perú)
├─ Crea entrada en public.empresas
├─ Asigna schema_name: "empresa_1"
├─ Encola task: crear_schema_empresa
│  ├─ CREATE SCHEMA empresa_1
│  ├─ CREATE todas las tablas
│  ├─ CREATE índices
│  └─ INSERT secuencias iniciales
├─ Crea usuario admin en public.usuarios
└─ Devuelve token JWT

Frontend:
└─ Redirige a dashboard
```

### 2. Crear y Enviar Factura a SUNAT

```
POST /api/facturas
{
  "cliente_id": 5,
  "items": [
    {"producto_id": 1, "cantidad": 2, "precio_unitario": 100}
  ],
  "total": 236  (200 + 36 IGV)
}

↓

Backend (FastAPI):
├─ Valida datos
├─ Crea factura con estado: "borrador"
├─ Asigna número_serie: "F001", número_comprobante: "000001"
├─ Encola task Celery: firmar_y_enviar_sunat
└─ Devuelve: {"factura_id": 1, "estado": "pendiente_firma"}

↓

Celery Worker (en background):
├─ Obtiene factura de BD en schema correcto
├─ Genera XML UBL 2.1:
│  ├─ Datos de empresa (RUC, razón social)
│  ├─ Datos de cliente (RUC/DNI)
│  ├─ Ítems con descripciones y montos
│  └─ Cálculos de IGV
├─ Carga certificado digital de empresa
├─ Firma XML criptográficamente (XAdES)
├─ Conecta a SUNAT vía WebService SOAP
├─ Envía: SendBill(fileName, xmlContent)
└─ Recibe respuesta

Si ACEPTADA:
├─ estado_sunat = "aceptada"
├─ numero_cdr = "123456789"
├─ respuesta_sunat = {resultado: "Aceptado", ...}
└─ Guarda en BD

Si RECHAZADA:
├─ estado_sunat = "rechazada"
├─ respuesta_sunat = {errores: [...]}
└─ Notifica al usuario en frontend

Si ERROR DE CONEXIÓN:
├─ intentos_sunat += 1
├─ proximo_intento_sunat = now + 30 min
├─ Celery reintentará automáticamente
└─ Usuario ve estado: "pendiente_envío"

↓

Usuario en Frontend:
├─ Hace polling: GET /api/facturas/1/estado-sunat
├─ Ve estado actualizado
└─ Si aceptada, puede descargar PDF
```

### 3. Convertir Cotización a Factura

```
POST /api/cotizaciones/5/convertir-a-factura

↓

Backend:
├─ Valida que cotización existe y estado es "aceptada"
├─ Copia datos de cotización
├─ Crea factura con mismo total y items
├─ Marca cotización como "convertida"
├─ Factura lista para enviar a SUNAT
└─ Devuelve factura_id

↓

Usuario en Frontend:
└─ Redirige a editar factura (puede ajustar si necesita)
└─ Botón "Enviar a SUNAT"
└─ Sigue flujo de envío
```

---

## 🔧 Especificaciones Técnicas

### Seguridad Multi-Tenant

1. **JWT Token incluye:**
   ```json
   {
     "sub": 1,              // usuario_id
     "empresa_id": 1,       // empresa del usuario
     "rol": "admin",
     "exp": 1234567890
   }
   ```

2. **Middleware en cada request:**
   - Valida JWT
   - Extrae empresa_id
   - Obtiene schema name de BD
   - Ejecuta: `SET search_path TO empresa_1, public`
   - Query solo ve datos de empresa_1

3. **Base de datos:**
   - Imposible acceder a otra empresa sin cambiar el schema
   - Cada query está automáticamente en el schema correcto

### Numeración de Facturas (SUNAT)

```
Formato: [SERIE]-[NÚMERO]
Ejemplo: F001-000001

- SERIE: Definida por empresa (F001, F002, B001, etc)
- NÚMERO: Secuencia 000001 a 999999

Tabla secuencias:
├─ tipo_documento: "01" (Factura), "03" (Boleta)
├─ serie: "F001", "F002"
└─ proximo_numero: incrementa cada vez

SUNAT requiere:
✅ Numeración consecutiva (no puede faltar números)
✅ No puede repetir número en misma serie
✅ Máximo 999999 por serie (después cambiar serie)
```

### Integración SUNAT

**Ambiente Beta (Testing):**
```
URL: https://e-beta.sunat.gob.pe/ords/f?p=730:3
Usuario SOL: Tu RUC (sin dígito verificador)
Contraseña: Tu contraseña SOL
```

**Ambiente Producción:**
```
URL: https://www.sunat.gob.pe/ords/f?p=730:3
Certificado digital: Requerido (no usuario/contraseña)
```

**Formato de Factura (XML UBL 2.1):**
- Namespace: `urn:oasis:names:specification:ubl:schema:xsd:Invoice-2`
- Versión: 2.1
- Caracteres especiales: UTF-8
- Firma: XAdES

### Códigos SUNAT Importantes

```
Tipo Documento:
├─ 01 = Factura
├─ 03 = Boleta
├─ 07 = Nota de Crédito
└─ 08 = Nota de Débito

Tipo de Cliente:
├─ RUC = Persona Jurídica
├─ DNI = Persona Natural
└─ OTROS = Domiciliados en el Exterior

Códigos de Rechazo (muestras):
├─ 01 = Error en RUC
├─ 02 = Error en DNI
├─ 1200 = Total de operación inválido
└─ Ver documentación SUNAT para lista completa
```

---

## 📈 Roadmap

### Fase 1: MVP (Enero-Febrero 2025)
- [x] Arquitectura multi-tenant
- [x] CRUD de productos, clientes, cotizaciones
- [ ] Emisión básica de facturas
- [ ] Integración SUNAT (firma digital)
- [ ] Autenticación JWT
- [ ] Frontend básico

### Fase 2: Features (Marzo-Abril 2025)
- [ ] Notas de crédito/débito
- [ ] Plantillas personalizables
- [ ] Reportes de ventas
- [ ] Integración contable
- [ ] API pública para terceros

### Fase 3: Enterprise (Mayo+ 2025)
- [ ] SSO (Single Sign-On)
- [ ] 2FA (Two-Factor Authentication)
- [ ] White-label
- [ ] Integración contable automática
- [ ] BI y analytics avanzados

---

## ⚙️ Configuración de Entorno

### Variables Requeridas (.env)

```env
# ===== DATABASE =====
DB_USER=facturacion
DB_PASSWORD=SecurePassword123!
DB_HOST=localhost
DB_PORT=5432
DB_NAME=facturacion_db

# ===== BACKEND =====
FASTAPI_ENV=development
SECRET_KEY=your-secret-key-min-32-chars-CHANGE-IN-PRODUCTION
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ===== REDIS =====
REDIS_URL=redis://localhost:6379/0

# ===== CELERY =====
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ===== SUNAT =====
AMBIENTE_SUNAT=beta  # o 'produccion'
RUTA_CERTIFICADO=/certs/certificado.p12
CONTRASEÑA_CERTIFICADO=tu-password-cert  # NO hardcodear en producción

# ===== FRONTEND =====
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_NAME=Facturación SUNAT
```

### Secrets en Producción

⚠️ **NUNCA** commits secrets a Git:
- Usar variables de entorno en servidor
- Usar secrets manager (AWS Secrets Manager, Hashicorp Vault)
- En producción: usar `.env` desde deployment service

---

## 🚢 Deployment

### Producción (Recomendado)

**Backend:**
- Hosting: DigitalOcean App Platform / AWS EC2 / Railway
- Database: AWS RDS PostgreSQL / DigitalOcean Managed
- Redis: DigitalOcean App Platform / AWS ElastiCache
- Workers: Same instance como backend (Celery)

**Frontend:**
- Hosting: Vercel (mejor para Next.js)
- CDN: Vercel Edge Network (incluido)
- Dominio: Vercel Domain / Custom domain

**Stack Completo:**
```bash
# Build images
docker build -t facturacion-backend:latest backend/
docker build -t facturacion-frontend:latest frontend/

# Push a registry (DockerHub, AWS ECR, etc)
docker push facturacion-backend:latest
docker push facturacion-frontend:latest

# Deploy en DigitalOcean/AWS/Heroku usando docker-compose.prod.yml
```

### Variables de Producción (Checklist)

- [ ] SECRET_KEY: Generar con `secrets.token_urlsafe(32)`
- [ ] DB_PASSWORD: Contraseña fuerte (AWS Secrets Manager)
- [ ] CERTIFICADO: Subido a servidor, no en Git
- [ ] CORS_ORIGINS: Actualizado con dominio real
- [ ] SSL/TLS: Certificado Let's Encrypt
- [ ] Backups: Automáticos diarios de BD
- [ ] Monitoring: Sentry para errores, DataDog para métricas
- [ ] Logs: Centralizados en ELK Stack o CloudWatch

---

## 🤝 Contribución

### Cómo Contribuir

1. Fork el repositorio
2. Crear rama: `git checkout -b feature/descripcion`
3. Commits: `git commit -m "feat: descripción clara"`
4. Push: `git push origin feature/descripcion`
5. Pull Request (describir cambios)

### Estándares

- Tests unitarios para nuevas features
- Documentación actualizada
- Seguir convenciones de código
- Code review antes de merge

### Testing

```bash
# Backend tests
pytest backend/tests/ -v

# Frontend tests
npm test

# Coverage
pytest --cov=app backend/tests/
```

---

## 📚 Recursos Adicionales

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Documentación SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentación Celery](https://docs.celeryproject.io/)
- [Documentación Next.js](https://nextjs.org/docs)
- [SUNAT Facturación Electrónica](https://www.sunat.gob.pe/)

---

## 📞 Soporte

- **Documentación:** `/docs` en el repositorio
- **Issues:** GitHub Issues
- **Discusiones:** GitHub Discussions
- **Email:** support@facturacion-saas.com

---

## 📄 Licencia

MIT License - Ver archivo `LICENSE`

---

## 👨‍💼 Autor

Desarrollado con ❤️ para empresas peruanas

**Versión Actual:** 1.0.0  
**Última actualización:** Enero 2025

---

## 🎯 Checklist para Nuevos Desarrolladores

Cuando se une alguien nuevo al proyecto:

- [ ] Clonar repositorio
- [ ] Instalar dependencias (backend + frontend)
- [ ] Crear archivo `.env` desde `.env.example`
- [ ] Iniciar PostgreSQL, Redis
- [ ] Ejecutar migraciones de BD
- [ ] Iniciar backend (FastAPI)
- [ ] Iniciar Celery worker
- [ ] Iniciar frontend (Next.js)
- [ ] Verificar health check: `curl http://localhost:8000/health`
- [ ] Leer ARQUITECTURA.md
- [ ] Leer este README completamente
- [ ] Hacer commit de cambio inicial

---


**Happy Coding! 🚀**