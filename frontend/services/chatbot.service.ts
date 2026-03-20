import { apiFetch } from "@/lib/api";
import type { ChatMessage } from "@/types/chatbot";

// ============================================================================
// Chatbot Service — Integración con Backend
// ============================================================================
// Conecta el chatbot del frontend con el endpoint POST /api/chat/.
// El token JWT se inyecta automáticamente vía apiFetch.
// ============================================================================

interface ChatApiResponse {
    message: string;
}

/**
 * Envía un mensaje al asistente y obtiene una respuesta.
 *
 * @param mensaje   - Texto del usuario
 * @param historial - Historial de la conversación (contexto para el LLM)
 * @returns Respuesta del asistente como string
 */
export async function enviarMensaje(
    mensaje: string,
    historial: ChatMessage[]
): Promise<string> {
    // Convertir historial al formato que espera el backend: { role, content }
    const history = historial.map((m) => ({
        role: m.role,
        content: m.content,
    }));

    const response = await apiFetch<ChatApiResponse>("/chat/", {
        method: "POST",
        body: JSON.stringify({ message: mensaje, history }),
    });

    return response.message;
}
