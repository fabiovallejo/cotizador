"use client";

import { AuthProvider } from "@/context/AuthContext";

/**
 * Wrapper client-side para poder usar AuthProvider
 * dentro del RootLayout (que es un Server Component).
 */
export function AuthProviderWrapper({
    children,
}: {
    children: React.ReactNode;
}) {
    return <AuthProvider>{children}</AuthProvider>;
}
