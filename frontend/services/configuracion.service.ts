import { apiFetch } from "@/lib/api";
import type {
    Perfil,
    ConfigEmpresa,
    CuentaBancaria,
    CuentaBancariaForm,
    UsuarioAdmin,
    CrearUsuarioForm,
    EditarUsuarioForm,
    AuditLogsResponse,
} from "@/types/configuracion";

// ============================================================================
// MI PERFIL
// ============================================================================

export async function obtenerPerfil(): Promise<Perfil> {
    return apiFetch<Perfil>("/empresa/usuarios/me");
}

export async function actualizarPerfil(data: {
    nombre?: string;
    apellido?: string;
}): Promise<Perfil> {
    return apiFetch<Perfil>("/empresa/usuarios/me", {
        method: "PUT",
        body: JSON.stringify(data),
    });
}

export async function cambiarPassword(data: {
    password_actual: string;
    password_nuevo: string;
}): Promise<{ mensaje: string }> {
    return apiFetch<{ mensaje: string }>("/empresa/usuarios/cambiar-password", {
        method: "PUT",
        body: JSON.stringify(data),
    });
}

// ============================================================================
// CONFIGURACIÓN EMPRESA
// ============================================================================

export async function obtenerConfigEmpresa(): Promise<ConfigEmpresa> {
    return apiFetch<ConfigEmpresa>("/empresa/configuracion");
}

export async function actualizarConfigEmpresa(
    data: Partial<ConfigEmpresa>
): Promise<ConfigEmpresa> {
    return apiFetch<ConfigEmpresa>("/empresa/configuracion", {
        method: "PUT",
        body: JSON.stringify(data),
    });
}

export async function subirLogo(file: File): Promise<{ logo_url: string }> {
    const formData = new FormData();
    formData.append("file", file);
    return apiFetch<{ logo_url: string }>("/empresa/logo", {
        method: "POST",
        body: formData,
    });
}

export async function eliminarLogo(): Promise<{ message: string }> {
    return apiFetch<{ message: string }>("/empresa/logo", {
        method: "DELETE",
    });
}

// ============================================================================
// CUENTAS BANCARIAS
// ============================================================================

export async function listarCuentasBancarias(): Promise<CuentaBancaria[]> {
    return apiFetch<CuentaBancaria[]>("/config/cuentas-bancarias");
}

export async function crearCuentaBancaria(
    data: CuentaBancariaForm
): Promise<CuentaBancaria> {
    return apiFetch<CuentaBancaria>("/config/cuentas-bancarias", {
        method: "POST",
        body: JSON.stringify(data),
    });
}

export async function actualizarCuentaBancaria(
    id: number,
    data: Partial<CuentaBancariaForm> & { activo?: boolean }
): Promise<CuentaBancaria> {
    return apiFetch<CuentaBancaria>(`/config/cuentas-bancarias/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
}

export async function eliminarCuentaBancaria(
    id: number
): Promise<CuentaBancaria> {
    return apiFetch<CuentaBancaria>(`/config/cuentas-bancarias/${id}`, {
        method: "DELETE",
    });
}

// ============================================================================
// USUARIOS (ADMIN)
// ============================================================================

export async function listarUsuarios(): Promise<UsuarioAdmin[]> {
    return apiFetch<UsuarioAdmin[]>("/empresa/usuarios");
}

export async function crearUsuario(
    data: CrearUsuarioForm
): Promise<UsuarioAdmin> {
    return apiFetch<UsuarioAdmin>("/empresa/usuarios", {
        method: "POST",
        body: JSON.stringify(data),
    });
}

export async function actualizarUsuario(
    id: number,
    data: EditarUsuarioForm
): Promise<UsuarioAdmin> {
    return apiFetch<UsuarioAdmin>(`/empresa/usuarios/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
}

export async function eliminarUsuario(id: number): Promise<UsuarioAdmin> {
    return apiFetch<UsuarioAdmin>(`/empresa/usuarios/${id}`, {
        method: "DELETE",
    });
}

// ============================================================================
// AUDIT LOGS
// ============================================================================

export async function obtenerAuditLogs(
    page: number = 1,
    limit: number = 20
): Promise<AuditLogsResponse> {
    return apiFetch<AuditLogsResponse>(
        `/config/audit-logs?page=${page}&limit=${limit}`
    );
}

