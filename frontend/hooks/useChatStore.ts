import { create } from "zustand";
import type { ChatMessage } from "@/types/chatbot";
import { enviarMensaje } from "@/services/chatbot.service";

// ============================================================================
// Chat Store — Zustand
// ============================================================================

interface ChatState {
    messages: ChatMessage[];
    isOpen: boolean;
    isLoading: boolean;
    hasUnread: boolean;

    toggleChat: () => void;
    openChat: () => void;
    closeChat: () => void;
    sendMessage: (content: string) => Promise<void>;
    clearChat: () => void;
}

/** Genera un ID único para cada mensaje */
const generateId = () =>
    `msg_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;

export const useChatStore = create<ChatState>((set, get) => ({
    messages: [],
    isOpen: false,
    isLoading: false,
    hasUnread: false,

    toggleChat: () =>
        set((state) => ({
            isOpen: !state.isOpen,
            hasUnread: state.isOpen ? state.hasUnread : false,
        })),

    openChat: () => set({ isOpen: true, hasUnread: false }),

    closeChat: () => set({ isOpen: false }),

    sendMessage: async (content: string) => {
        const trimmed = content.trim();
        if (!trimmed || get().isLoading) return;

        // Agregar mensaje del usuario
        const userMessage: ChatMessage = {
            id: generateId(),
            role: "user",
            content: trimmed,
            timestamp: new Date(),
        };

        set((state) => ({
            messages: [...state.messages, userMessage],
            isLoading: true,
        }));

        try {
            // Obtener respuesta del asistente
            const currentMessages = get().messages;
            const response = await enviarMensaje(trimmed, currentMessages);

            const assistantMessage: ChatMessage = {
                id: generateId(),
                role: "assistant",
                content: response,
                timestamp: new Date(),
            };

            set((state) => ({
                messages: [...state.messages, assistantMessage],
                isLoading: false,
                hasUnread: !state.isOpen,
            }));
        } catch {
            // En caso de error, agregar mensaje de error
            const errorMessage: ChatMessage = {
                id: generateId(),
                role: "assistant",
                content:
                    "Lo siento, ha ocurrido un error. Por favor intenta de nuevo.",
                timestamp: new Date(),
            };

            set((state) => ({
                messages: [...state.messages, errorMessage],
                isLoading: false,
            }));
        }
    },

    clearChat: () => set({ messages: [], isLoading: false }),
}));
