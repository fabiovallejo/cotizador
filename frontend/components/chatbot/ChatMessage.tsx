"use client";

import type { ChatMessage as ChatMessageType } from "@/types/chatbot";

// ============================================================================
// ChatMessage — Burbuja individual de mensaje
// ============================================================================

interface ChatMessageProps {
    message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
    const isUser = message.role === "user";

    const time = new Date(message.timestamp).toLocaleTimeString("es-PE", {
        hour: "2-digit",
        minute: "2-digit",
    });

    return (
        <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-5`}>
            <div
                className={`relative max-w-[80%] px-4 py-2.5 rounded-2xl text-[13px] leading-relaxed shadow-sm ${isUser
                    ? "bg-[#2E66F6] text-white rounded-br-md"
                    : "bg-gray-100 dark:bg-white/10 text-gray-800 dark:text-gray-200 rounded-bl-md"
                    }`}
            >
                <p className="whitespace-pre-wrap break-words">{message.content}</p>
                <span
                    className={`block mt-1 text-[10px] ${isUser
                        ? "text-blue-200"
                        : "text-gray-400 dark:text-gray-500"
                        }`}
                >
                    {time}
                </span>
            </div>
        </div>
    );
}

// ============================================================================
// TypingIndicator — Animación de "escribiendo..."
// ============================================================================

export function TypingIndicator() {
    return (
        <div className="flex justify-start mb-5">
            <div className="bg-gray-100 dark:bg-white/10 px-4 py-3 rounded-2xl rounded-bl-md">
                <div className="flex items-center gap-1">
                    <span className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
                    <span className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
                    <span className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" />
                </div>
            </div>
        </div>
    );
}
