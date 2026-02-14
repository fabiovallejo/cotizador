// ============================================================================
// Configuración — Tipos
// ============================================================================

/** Perfil del usuario autenticado */
export interface Perfil {
    id: number;
    email: string;
    nombre: string;
    apellido?: string;
    rol: string;
    estado: string;
    empresa_id: number;
    created_at: string;
    ultimo_login?: string;
}

/** Configuración de la empresa */
export interface ConfigEmpresa {
    id: number;
    empresa_id: number;
    serie_factura?: string;
    serie_boleta?: string;
    serie_nc?: string;
    serie_nd?: string;
    ruta_certificado?: string;
    logo_url?: string;
    telefono?: string;
    email?: string;
    created_at?: string;
    updated_at?: string;
}

/** Cuenta Bancaria */
export interface CuentaBancaria {
    id: number;
    empresa_id: number;
    nombre_banco: string;
    numero_cuenta: string;
    cci?: string;
    moneda: string;
    tipo_cuenta: string;
    titular: string;
    activo: boolean;
    created_at: string;
    updated_at: string;
}

export interface CuentaBancariaForm {
    nombre_banco: string;
    numero_cuenta: string;
    cci?: string;
    moneda: string;
    tipo_cuenta: string;
    titular: string;
}

/** Usuario para admin */
export interface UsuarioAdmin {
    id: number;
    empresa_id: number;
    email: string;
    nombre: string;
    apellido?: string;
    rol: string;
    estado: string;
    created_at: string;
    updated_at: string;
}

export interface CrearUsuarioForm {
    email: string;
    nombre: string;
    apellido?: string;
    password: string;
    rol: string;
}

export interface EditarUsuarioForm {
    nombre?: string;
    apellido?: string;
    rol?: string;
    estado?: string;
}

/** Audit log */
export interface AuditLog {
    id: number;
    usuario_id: number;
    usuario_nombre: string;
    accion: string;
    tabla: string;
    registro_id?: number;
    cambios?: string;
    descripcion?: string;
    ip_usuario?: string;
    created_at?: string;
}

export interface AuditLogsResponse {
    items: AuditLog[];
    total: number;
    page: number;
    limit: number;
    total_pages: number;
}
