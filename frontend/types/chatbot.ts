// ============================================================================
// Tipos del Chatbot Copiloto
// ============================================================================

/** Rol del participante en la conversación */
export type ChatRole = "user" | "assistant";

/** Mensaje individual en la conversación */
export interface ChatMessage {
    id: string;
    role: ChatRole;
    content: string;
    timestamp: Date;
}

/** Estado de la conversación completa */
export interface ChatConversation {
    messages: ChatMessage[];
    isOpen: boolean;
    isLoading: boolean;
}
