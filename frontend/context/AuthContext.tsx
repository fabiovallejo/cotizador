'use client';

import React, { createContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export interface User {
    usuario_id: number;
    empresa_id: number;
    rol: string;
    email: string;
}

export interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (email: string, password: string) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        // Verificar si hay token guardado
        const token = localStorage.getItem('access_token');
        if (token) {
            // Aquí puedes validar el token con el backend
            // Por ahora lo dejamos como está
        }
        setLoading(false);
    }, []);

    const login = async (email: string, password: string) => {
        // TODO: Implementar login con backend
        // const response = await api.post('/auth/login', { email, password });
        // localStorage.setItem('access_token', response.data.access_token);
        // setUser(response.data.user);
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        setUser(null);
        router.push('/auth/login');
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, isAuthenticated: !!user }}>
            {children}
        </AuthContext.Provider>
    );
}