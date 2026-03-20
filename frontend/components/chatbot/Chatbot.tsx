"use client";

import { ChatBubble } from "./ChatBubble";
import { ChatWindow } from "./ChatWindow";

// ============================================================================
// Chatbot — Componente orquestador
// ============================================================================
// Renderiza el FAB flotante y el panel de chat.
// Se monta una sola vez en el DashboardLayout y persiste en toda la app.
// ============================================================================

export function Chatbot() {
    return (
        <>
            <ChatWindow />
            <ChatBubble />
        </>
    );
}
