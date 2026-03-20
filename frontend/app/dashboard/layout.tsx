"use client";

import { Sidebar } from "@/components/layout/Sidebar";
import { ThemeProvider } from "@/components/theme-provider";
import { Chatbot } from "@/components/chatbot/Chatbot";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
            <div className="flex min-h-screen bg-[#f8fafc] dark:bg-[#1a1f24] transition-colors duration-300">
                <Sidebar />
                <main className="flex-1 ml-20 p-8 transition-all duration-300 ease-in-out">
                    {children}
                </main>
                <Chatbot />
            </div>
        </ThemeProvider>
    );
}
