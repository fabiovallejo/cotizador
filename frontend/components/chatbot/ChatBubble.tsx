"use client";

import { MessageCircle, X } from "lucide-react";
import { useChatStore } from "@/hooks/useChatStore";

// ============================================================================
// ChatBubble — Botón flotante (FAB) del chatbot
// ============================================================================

export function ChatBubble() {
    const { isOpen, toggleChat, hasUnread } = useChatStore();

    return (
        <button
            onClick={toggleChat}
            aria-label={isOpen ? "Cerrar asistente" : "Abrir asistente"}
            className={`
                fixed bottom-6 right-6 z-[60]
                w-14 h-14 rounded-full
                bg-gradient-to-tr from-[#FF7043] to-[#FF8A65]
                text-white shadow-lg shadow-orange-500/30
                flex items-center justify-center
                transition-all duration-300 ease-in-out
                hover:scale-110 hover:shadow-xl hover:shadow-orange-500/40
                active:scale-95
                cursor-pointer
            `}
        >
            {/* Ícono con transición de rotación */}
            <div
                className={`transition-transform duration-300 ${isOpen ? "rotate-90 scale-110" : "rotate-0"
                    }`}
            >
                {isOpen ? (
                    <X className="w-6 h-6" />
                ) : (
                    <MessageCircle className="w-6 h-6" />
                )}
            </div>

            {/* Badge de no leídos */}
            {hasUnread && !isOpen && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-[10px] font-bold text-white shadow-sm animate-pulse" />
            )}
        </button>
    );
}
