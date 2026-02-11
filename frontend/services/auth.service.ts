import { apiFetch } from "@/lib/api";
import type { LoginResponse, User } from "@/types/auth";

/**
 * Llama al endpoint de login y retorna el token.
 * No guarda nada en localStorage — eso lo hace el AuthContext.
 */
export async function loginRequest(
    email: string,
    password: string
): Promise<LoginResponse> {
    return apiFetch<LoginResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
    });
}

/**
 * Obtiene los datos del usuario autenticado (valida que el token sea válido).
 */
export async function obtenerUsuarioActual(): Promise<User> {
    return apiFetch<User>("/auth/me");
}

/**
 * Cierra sesión: limpia el token y redirige al login.
 */
export function logout(): void {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
}
