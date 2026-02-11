// ============================================================================
// Auth
// ============================================================================

/** Respuesta del endpoint POST /auth/login */
export interface LoginResponse {
    access_token: string;
    token_type: string;
}

/** Respuesta del endpoint GET /auth/me */
export interface User {
    usuario_id: number;
    empresa_id: number;
    rol: string;
    db_schema: string;
}

// ============================================================================
// API
// ============================================================================

/** Estructura de error estándar de la API */
export interface ApiError {
    detail: string;
}
