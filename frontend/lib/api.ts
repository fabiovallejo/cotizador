const API_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

/**
 * Wrapper de fetch para llamadas a la API.
 * - Inyecta token de autenticación automáticamente
 * - Maneja errores 401 (sesión expirada) y 403 (sin permisos)
 * - Retorna el JSON tipado
 */
export async function apiFetch<T = unknown>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const token = localStorage.getItem("access_token");

    const headers: HeadersInit = {};

    // Solo agregar Content-Type si no es FormData (fetch lo maneja automáticamente)
    if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: {
            ...headers,
            ...(options.headers || {}),
        },
    });

    let data: T | null;
    try {
        data = await res.json();
    } catch {
        data = null;
    }

    if (res.status === 401) {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
        throw new Error("Sesión expirada");
    }

    if (res.status === 403) {
        throw new Error("No tienes permisos");
    }

    if (!res.ok) {
        const errorData = data as Record<string, string> | null;
        throw new Error(
            errorData?.detail || errorData?.message || "Error en la API"
        );
    }

    return data as T;
}

/**
 * Wrapper de fetch para descargar archivos binarios (PDF, etc).
 * - Inyecta token de autenticación automáticamente
 * - Maneja errores 401/403
 * - Retorna un Blob
 */
export async function apiFetchBlob(
    endpoint: string,
    options: RequestInit = {}
): Promise<Blob> {
    const token = localStorage.getItem("access_token");

    const headers: HeadersInit = {};

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: {
            ...headers,
            ...(options.headers || {}),
        },
    });

    if (res.status === 401) {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
        throw new Error("Sesión expirada");
    }

    if (res.status === 403) {
        throw new Error("No tienes permisos");
    }

    if (!res.ok) {
        let detail = "Error al descargar archivo";
        try {
            const errData = await res.json();
            detail = errData?.detail || errData?.message || detail;
        } catch { /* ignore */ }
        throw new Error(detail);
    }

    return res.blob();
}
