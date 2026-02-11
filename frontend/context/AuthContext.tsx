"use client";

import React, { createContext, useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import type { User } from "@/types/auth";
import {
    loginRequest,
    obtenerUsuarioActual,
    logout as authLogout,
} from "@/services/auth.service";

// ============================================================================
// Tipos del contexto
// ============================================================================

export interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (email: string, password: string) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============================================================================
// Provider
// ============================================================================

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    /**
     * Al montar: si hay token guardado, valida con /auth/me
     * para restaurar la sesión del usuario.
     */
    useEffect(() => {
        const token = localStorage.getItem("access_token");
        if (!token) {
            setLoading(false);
            return;
        }

        obtenerUsuarioActual()
            .then((userData) => {
                setUser(userData);
            })
            .catch(() => {
                // Token inválido o expirado — limpiar
                localStorage.removeItem("access_token");
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    /**
     * Login: llama al backend, guarda el token, obtiene datos del usuario,
     * y redirige al dashboard de su empresa.
     */
    const login = useCallback(
        async (email: string, password: string) => {
            const data = await loginRequest(email, password);
            localStorage.setItem("access_token", data.access_token);

            // Obtener datos del usuario
            const userData = await obtenerUsuarioActual();
            setUser(userData);

            // Redirigir al dashboard
            router.push("/dashboard");
        },
        [router]
    );

    /**
     * Logout: limpia estado y redirige al login.
     */
    const logout = useCallback(() => {
        setUser(null);
        authLogout();
    }, []);

    return (
        <AuthContext.Provider
            value={{ user, loading, login, logout, isAuthenticated: !!user }}
        >
            {children}
        </AuthContext.Provider>
    );
}