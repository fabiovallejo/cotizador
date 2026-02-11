"use client";

import { useState, FormEvent } from "react";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<{
        type: "success" | "error";
        text: string;
    } | null>(null);

    const { login } = useAuth();

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setMessage(null);
        setLoading(true);

        try {
            await login(email, password);
            setMessage({ type: "success", text: "¡Inicio de sesión exitoso!" });
        } catch (err: unknown) {
            const errorMessage =
                err instanceof Error
                    ? err.message
                    : "Error al conectar con el servidor";
            setMessage({ type: "error", text: errorMessage });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen">
            {/* Left Side - Artistic / Branding */}
            <div className="hidden relative lg:flex lg:w-[45%] flex-col justify-center items-start bg-[#263238] overflow-hidden px-16 py-12">
                {/* Abstract shapes & Gradients */}
                <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-gradient-to-b from-[#2E66F6]/10 to-[#FF7043]/10 rounded-full blur-3xl translate-x-1/2 -translate-y-1/2 pointer-events-none" />
                <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-[#FF7043]/5 rounded-full blur-[100px] -translate-x-1/3 translate-y-1/3 pointer-events-none" />

                {/* Mesh pattern overlay */}
                <div className="absolute inset-0 opacity-[0.07]"
                    style={{
                        backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)',
                        backgroundSize: '32px 32px'
                    }}
                />

                {/* Content Container - Centered Vertically via Flex Column */}
                <div className="relative z-10 w-full max-w-lg mx-auto flex flex-col gap-12">

                    {/* Brand Area */}
                    <div>
                        <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-md mb-8">
                            <span className="flex h-2.5 w-2.5 rounded-full bg-[#FF7043] animate-pulse"></span>
                            <span className="text-xs font-medium text-white/80 tracking-wide uppercase">Facturador SaaS</span>
                        </div>
                        <h1 className="text-5xl xl:text-6xl font-bold text-white tracking-tight leading-[1.1]">
                            Gestiona tu<br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FF7043] to-[#2E66F6]">
                                negocio
                            </span>{" "}
                            sin<br />
                            límites.
                        </h1>
                    </div>

                    {/* Abstract "Card" Visuals showing UI elements */}
                    <div className="perspective-[1000px]">
                        <div className="relative w-full aspect-[16/10] bg-gradient-to-br from-white/10 to-white/5 rounded-2xl border border-white/10 backdrop-blur-xl p-8 transform rotate-y-6 rotate-x-3 hover:rotate-y-0 hover:rotate-x-0 transition-transform duration-700 ease-out shadow-2xl shadow-black/20 group">
                            {/* Shine effect */}
                            <div className="absolute inset-0 bg-gradient-to-tr from-white/0 via-white/5 to-white/0 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none rounded-2xl" />

                            {/* Fake UI Elements inside the card */}
                            <div className="flex items-center justify-between mb-8">
                                <div className="w-1/3 h-4 bg-white/20 rounded-full" />
                                <div className="flex gap-2">
                                    <div className="w-3 h-3 rounded-full bg-red-400/50" />
                                    <div className="w-3 h-3 rounded-full bg-yellow-400/50" />
                                    <div className="w-3 h-3 rounded-full bg-green-400/50" />
                                </div>
                            </div>
                            <div className="space-y-5">
                                <div className="w-full h-32 bg-gradient-to-r from-[#2E66F6]/10 to-transparent rounded-xl border border-white/5 flex items-end p-4">
                                    {/* Tiny Chart Bars */}
                                    <div className="flex items-end gap-2 w-full h-16">
                                        <div className="w-full bg-[#2E66F6]/30 h-[40%] rounded-sm" />
                                        <div className="w-full bg-[#2E66F6]/40 h-[70%] rounded-sm" />
                                        <div className="w-full bg-[#2E66F6]/60 h-[50%] rounded-sm" />
                                        <div className="w-full bg-[#FF7043] h-[85%] rounded-sm shadow-[0_0_10px_rgba(255,112,67,0.5)]" />
                                    </div>
                                </div>
                                <div className="flex gap-4">
                                    <div className="w-1/2 h-20 bg-white/5 rounded-xl border border-white/5" />
                                    <div className="w-1/2 h-20 bg-white/5 rounded-xl border border-white/5" />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Footer info */}
                    <div className="flex gap-8 text-white/40 text-sm font-medium pt-8 border-t border-white/5">
                        <span>© 2026 Facturador</span>
                        <a href="#" className="hover:text-white transition-colors">Ayuda</a>
                        <a href="#" className="hover:text-white transition-colors">Contacto</a>
                    </div>

                </div>
            </div>

            {/* Right Side - Login Form - Cleaner & Modern */}
            <div className="flex-1 flex flex-col justify-center items-center p-8 lg:p-12 bg-[#f8fafc] relative">
                <div className="w-full max-w-lg bg-white rounded-3xl shadow-sm border border-gray-100 p-8 md:p-12">
                    {/* Mobile Logo */}
                    <div className="lg:hidden mb-8 flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-[#FF7043]"></div>
                        <span className="font-bold text-xl text-[#263238]">Facturador</span>
                    </div>

                    <div className="mb-10 text-center lg:text-left">
                        <h2 className="text-3xl font-bold text-[#263238] tracking-tight mb-3">¡Hola de nuevo!</h2>
                        <p className="text-[#78889B] text-[15px]">Por favor, ingresa tus datos para continuar.</p>
                    </div>

                    {/* Message Alert */}
                    {message && (
                        <div
                            className={`mb-6 flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium animate-in fade-in slide-in-from-top-2 duration-300 ${message.type === "success"
                                ? "bg-green-50 text-green-700 border border-green-100"
                                : "bg-red-50 text-red-700 border border-red-100"
                                }`}
                        >
                            {message.type === "success" ? (
                                <svg className="shrink-0 w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12" /></svg>
                            ) : (
                                <svg className="shrink-0 w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" /></svg>
                            )}
                            {message.text}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
                        <div className="group">
                            <label className="block text:[13px] font-semibold text-[#263238] mb-2 ml-1">Email</label>
                            <div className="relative transition-all duration-200 focus-within:transform focus-within:scale-[1.01]">
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="nombre@ejemplo.com"
                                    className="w-full h-[52px] rounded-xl border border-gray-200 bg-[#fafbfc] px-4 text-[#263238] placeholder-gray-400 outline-none transition-all focus:bg-white focus:border-[#2E66F6] focus:ring-4 focus:ring-[#2E66F6]/5"
                                    required
                                />
                            </div>
                        </div>

                        <div className="group">
                            <label className="block text:[13px] font-semibold text-[#263238] mb-2 ml-1">Contraseña</label>
                            <div className="relative transition-all duration-200 focus-within:transform focus-within:scale-[1.01]">
                                <input
                                    type={showPassword ? "text" : "password"}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className="w-full h-[52px] rounded-xl border border-gray-200 bg-[#fafbfc] px-4 pr-12 text-[#263238] placeholder-gray-400 outline-none transition-all focus:bg-white focus:border-[#2E66F6] focus:ring-4 focus:ring-[#2E66F6]/5"
                                    required
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-[#263238] transition-colors"
                                >
                                    {showPassword ? (
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" /><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" /><line x1="1" y1="1" x2="23" y2="23" /></svg>
                                    ) : (
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></svg>
                                    )}
                                </button>
                            </div>
                            <div className="flex justify-end mt-2">
                                <button type="button" className="text-sm font-medium text-[#2E66F6] hover:text-[#1a4fd6] transition-colors">
                                    ¿Olvidaste tu contraseña?
                                </button>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="mt-2 w-full h-[52px] rounded-xl bg-gradient-to-r from-[#263238] to-[#1e282d] text-white font-semibold text-[15px] shadow-lg shadow-gray-200 hover:to-black hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200 flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <>
                                    Iniciar Sesión
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="opacity-80"><line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" /></svg>
                                </>
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}
