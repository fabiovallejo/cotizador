"use client";

import { useRef, useEffect, useState } from "react";
import { Minus, Trash2, Send, Sparkles } from "lucide-react";
import { useChatStore } from "@/hooks/useChatStore";
import { ChatMessage, TypingIndicator } from "./ChatMessage";

// ============================================================================
// ChatWindow — Panel de conversación expandible
// ============================================================================

export function ChatWindow() {
    const { messages, isOpen, isLoading, sendMessage, closeChat, clearChat } =
        useChatStore();
    const [input, setInput] = useState("");
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Auto-scroll al último mensaje
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isLoading]);

    // Focus en el input cuando se abre
    useEffect(() => {
        if (isOpen) {
            setTimeout(() => inputRef.current?.focus(), 300);
        }
    }, [isOpen]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;
        sendMessage(input);
        setInput("");
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <div
            className={`
                fixed bottom-24 right-6 z-[59]
                w-[450px] h-[680px]
                flex flex-col
                rounded-2xl overflow-hidden
                border border-gray-200 dark:border-white/10
                bg-white/95 dark:bg-[#1f2937]/95
                backdrop-blur-xl
                shadow-2xl shadow-black/10 dark:shadow-black/40
                transition-all duration-300 ease-in-out origin-bottom-right
                ${isOpen
                    ? "scale-100 opacity-100 translate-y-0 pointer-events-auto"
                    : "scale-95 opacity-0 translate-y-4 pointer-events-none"
                }
                max-[480px]:w-[calc(100vw-2rem)] max-[480px]:right-4 max-[480px]:left-4
                max-[480px]:h-[70vh] max-[480px]:bottom-20
            `}
        >
            {/* ----------------------------------------------------------------
                Header
            ---------------------------------------------------------------- */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-white/5 bg-gradient-to-r from-[#2E66F6]/5 to-transparent dark:from-[#2E66F6]/10 shrink-0">
                <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#FF7043] to-[#FF8A65] flex items-center justify-center shadow-sm shadow-orange-500/20">
                        <Sparkles className="w-4 h-4 text-white" />
                    </div>
                    <div>
                        <h3 className="text-[13px] font-semibold text-gray-900 dark:text-white leading-tight">
                            Disecodcito
                        </h3>
                        <span className="text-[10px] text-gray-400 dark:text-gray-500 flex items-center gap-1">
                            <span className="w-1.5 h-1.5 bg-green-500 rounded-full inline-block" />
                            En línea
                        </span>
                    </div>
                </div>

                <div className="flex items-center gap-1">
                    {messages.length > 0 && (
                        <button
                            onClick={clearChat}
                            className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10 transition-all duration-200"
                            title="Limpiar conversación"
                        >
                            <Trash2 className="w-4 h-4" />
                        </button>
                    )}
                    <button
                        onClick={closeChat}
                        className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/5 transition-all duration-200"
                        title="Minimizar"
                    >
                        <Minus className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* ----------------------------------------------------------------
                Messages Area
            ---------------------------------------------------------------- */}
            <div className="flex-1 overflow-y-auto px-4 py-4 scroll-smooth scrollbar-thin scrollbar-thumb-gray-200 dark:scrollbar-thumb-gray-700">
                {messages.length === 0 ? (
                    // Estado vacío — Mensaje de bienvenida
                    <div className="flex flex-col items-center justify-center h-full text-center px-6">
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-[#FF7043]/10 to-[#FF8A65]/10 dark:from-[#FF7043]/20 dark:to-[#FF8A65]/20 flex items-center justify-center mb-4">
                            <Sparkles className="w-7 h-7 text-[#FF7043]" />
                        </div>
                        <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-1.5">
                            ¡Hola! 👋
                        </h4>
                        <p className="text-[12px] text-gray-500 dark:text-gray-400 leading-relaxed">
                            Soy Disecodcito, tu asistente de cotizaciones. Pregúntame sobre
                            cotizaciones, clientes, productos, reportes, o analisis de información.
                        </p>

                        {/* Sugerencias rápidas */}
                        <div className="mt-5 flex flex-wrap gap-2 justify-center">
                            {[
                                "Creame una cotización",
                                "Creame un cliente",
                                "Creame un producto",
                                "Dame tus conclusiones de los reportes de este mes"
                            ].map((suggestion) => (
                                <button
                                    key={suggestion}
                                    onClick={() => sendMessage(suggestion)}
                                    className="px-3 py-1.5 text-[11px] font-medium rounded-full border border-gray-200 dark:border-white/10 text-gray-600 dark:text-gray-400 hover:border-[#2E66F6] hover:text-[#2E66F6] dark:hover:border-[#FF7043] dark:hover:text-[#FF7043] transition-all duration-200 hover:bg-blue-50/50 dark:hover:bg-white/5"
                                >
                                    {suggestion}
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <>
                        {messages.map((msg) => (
                            <ChatMessage key={msg.id} message={msg} />
                        ))}
                        {isLoading && <TypingIndicator />}
                    </>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* ----------------------------------------------------------------
                Input Area
            ---------------------------------------------------------------- */}
            <form
                onSubmit={handleSubmit}
                className="px-4 py-3 border-t border-gray-100 dark:border-white/5 shrink-0"
            >
                <div className="flex items-center gap-2 bg-gray-50 dark:bg-white/5 rounded-xl px-3 py-1.5 border border-gray-200/50 dark:border-white/5 focus-within:border-[#2E66F6] dark:focus-within:border-[#FF7043] transition-colors duration-200">
                    <input
                        ref={inputRef}
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Escribe tu pregunta..."
                        disabled={isLoading}
                        className="flex-1 bg-transparent text-[13px] text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 outline-none disabled:opacity-50 py-1.5"
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        className="p-2 rounded-lg text-white bg-[#2E66F6] hover:bg-[#2558d4] disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-200 active:scale-95 shrink-0"
                    >
                        <Send className="w-4 h-4" />
                    </button>
                </div>
                <p className="mt-1.5 text-center text-[10px] text-gray-400 dark:text-gray-600">
                    Powered by AI · Las respuestas pueden contener errores
                </p>
            </form>
        </div>
    );
}
