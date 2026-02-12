"use client";

import { useAuth } from "@/hooks/useAuth";
import { useTheme } from "next-themes";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import {
    LayoutDashboard,
    FileText,
    Users,
    Package,
    Settings,
    LogOut,
    Sun,
    Moon,
    ChevronRight,
    User,
    History,
    CircleHelp,
    Files,
    Briefcase,
} from "lucide-react";

const MENU_ITEMS = [
    {
        title: "Dashboard",
        href: "/dashboard",
        icon: LayoutDashboard,
    },
    {
        title: "Documentos",
        icon: FileText,
        href: "/dashboard/documentos",
        submenu: [
            { title: "Facturas", href: "/dashboard/documentos/facturas", icon: Files },
            { title: "Cotizaciones", href: "/dashboard/documentos/cotizaciones", icon: FileText },
        ],
    },
    {
        title: "Clientes",
        href: "/dashboard/clientes",
        icon: Users,
    },
    {
        title: "Productos",
        href: "/dashboard/productos",
        icon: Package,
    },
];

export function Sidebar() {
    const { user, logout } = useAuth();
    const { theme, setTheme } = useTheme();
    const [isExpanded, setIsExpanded] = useState(false);
    const pathname = usePathname();
    const [openSubmenu, setOpenSubmenu] = useState<string | null>(null);
    const [mounted, setMounted] = useState(false);

    useEffect(() => setMounted(true), []);

    const toggleSubmenu = (title: string) => {
        if (!isExpanded) {
            setIsExpanded(true);
            setOpenSubmenu(title);
        } else {
            setOpenSubmenu(openSubmenu === title ? null : title);
        }
    };

    return (
        <aside
            className={`fixed left-0 top-0 z-50 h-screen transition-all duration-300 ease-in-out flex flex-col border-r border-gray-200 dark:border-white/5 bg-white/90 dark:bg-[#1f2937]/95 backdrop-blur-xl overflow-x-hidden ${isExpanded ? "w-[260px] shadow-2xl shadow-gray-200/50 dark:shadow-none" : "w-[72px]"
                }`}
            onMouseEnter={() => setIsExpanded(true)}
            onMouseLeave={() => {
                setIsExpanded(false);
                setOpenSubmenu(null);
            }}
        >
            {/* 
        --------------------------------------------------------------------------
        Header
        --------------------------------------------------------------------------
      */}
            <div className="h-20 flex items-center px-4 relative shrink-0">
                <div className="flex items-center gap-3 w-full overflow-hidden">
                    {/* Logo Icon Container */}
                    <div className="relative shrink-0 w-10 h-10 flex items-center justify-center">
                        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-[#FF7043] to-[#FF8A65] flex items-center justify-center text-white shadow-md shadow-orange-500/20">
                            <Briefcase className="w-5 h-5 stroke-[2.5]" />
                        </div>
                    </div>

                    <div className={`flex flex-col whitespace-nowrap transition-all duration-300 ${isExpanded ? "opacity-100 max-w-[150px] ml-1" : "opacity-0 max-w-0"}`}>
                        <span className="font-bold text-lg text-gray-900 dark:text-white tracking-tight leading-none">
                            Facturador
                        </span>
                        <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest">
                            Enterprise
                        </span>
                    </div>
                </div>
            </div>

            {/* 
        --------------------------------------------------------------------------
        Navegación principal
        --------------------------------------------------------------------------
      */}
            <nav className="flex-1 overflow-y-auto overflow-x-hidden px-3 py-2 space-y-1 scrollbar-none">
                {MENU_ITEMS.map((item) => {
                    const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
                    const hasSubmenu = item.submenu && item.submenu.length > 0;
                    const isSubmenuOpen = openSubmenu === item.title;
                    const href = item.href;

                    return (
                        <div key={item.title}>
                            {hasSubmenu ? (
                                <button
                                    onClick={() => toggleSubmenu(item.title)}
                                    className={`group relative w-full flex items-center h-10 px-2.5 rounded-lg transition-all duration-200 outline-none ${isActive || isSubmenuOpen
                                        ? "bg-blue-50 dark:bg-white/5 text-[#2E66F6] dark:text-white"
                                        : "text-gray-500 dark:text-gray-400 hover:bg-gray-100/50 dark:hover:bg-white/5 hover:text-gray-900 dark:hover:text-white"
                                        }`}
                                >
                                    <div className="shrink-0 w-5 h-5 flex items-center justify-center">
                                        <item.icon className={`w-5 h-5 transition-colors duration-200 ${isActive ? "text-[#2E66F6] dark:text-[#FF7043]" : "text-gray-400 group-hover:text-gray-600 dark:text-gray-500 dark:group-hover:text-gray-300"}`} />
                                    </div>

                                    <span className={`ml-3 font-medium text-[13px] whitespace-nowrap overflow-hidden transition-all duration-300 origin-left ${isExpanded ? "opacity-100 max-w-[150px]" : "opacity-0 max-w-0"
                                        }`}>
                                        {item.title}
                                    </span>

                                    <ChevronRight className={`ml-auto w-4 h-4 text-gray-400 transition-all duration-300 ${isSubmenuOpen ? "rotate-90 text-[#2E66F6]" : ""} ${isExpanded ? "opacity-100" : "opacity-0 hidden"}`} />
                                </button>
                            ) : (
                                <Link
                                    href={href}
                                    className={`group relative w-full flex items-center h-10 px-2.5 rounded-lg transition-all duration-200 outline-none ${isActive
                                        ? "bg-blue-50 dark:bg-white/10 text-[#2E66F6] dark:text-white font-semibold"
                                        : "text-gray-500 dark:text-gray-400 hover:bg-gray-100/50 dark:hover:bg-white/5 hover:text-gray-900 dark:hover:text-white"
                                        }`}
                                >
                                    <div className="shrink-0 w-5 h-5 flex items-center justify-center">
                                        <item.icon className={`w-5 h-5 transition-colors duration-200 ${isActive ? "text-[#2E66F6] dark:text-white" : "text-gray-400 group-hover:text-gray-600 dark:text-gray-500 dark:group-hover:text-gray-300"}`} />
                                    </div>

                                    <span className={`ml-3 text-[13px] whitespace-nowrap overflow-hidden transition-all duration-300 origin-left ${isExpanded ? "opacity-100 max-w-[150px]" : "opacity-0 max-w-0"
                                        }`}>
                                        {item.title}
                                    </span>


                                    {isActive && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-[#2E66F6] rounded-r-full" />}
                                </Link>
                            )}

                            {/* --- Submenu Items --- */}
                            <div className={`overflow-hidden transition-all duration-300 ease-in-out ${hasSubmenu && isExpanded && isSubmenuOpen ? "max-h-40 opacity-100 mt-1" : "max-h-0 opacity-0"}`}>
                                <div className="space-y-0.5 py-1">
                                    {item.submenu?.map((sub) => (
                                        <Link
                                            key={sub.title}
                                            href={sub.href}
                                            className="flex items-center gap-3 pl-10 pr-3 py-2 rounded-lg text-[13px] text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-white/5 transition-all duration-200"
                                        >
                                            <div className="w-1 h-1 rounded-full bg-gray-300 dark:bg-white/20" />
                                            <span>{sub.title}</span>
                                        </Link>
                                    ))}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </nav>

            {/* 
        --------------------------------------------------------------------------
        Footer 
        --------------------------------------------------------------------------
      */}
            <div className="p-3 space-y-1 relative border-t border-gray-100 dark:border-white/5 shrink-0">

                <button
                    onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                    className="w-full flex items-center h-10 px-2.5 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100/50 dark:hover:bg-white/5 hover:text-gray-900 dark:hover:text-white transition-all duration-200 overflow-hidden"
                >
                    <div className="shrink-0 w-5 h-5 flex items-center justify-center">
                        {mounted && (theme === "dark"
                            ? <Sun className="w-[18px] h-[18px]" />
                            : <Moon className="w-[18px] h-[18px]" />
                        )}
                    </div>
                    <span className={`ml-3 font-medium text-[13px] whitespace-nowrap overflow-hidden transition-all duration-300 ${isExpanded ? "opacity-100 max-w-[150px]" : "opacity-0 max-w-0"}`}>
                        {mounted ? (theme === "dark" ? "Modo Claro" : "Modo Oscuro") : "Tema"}
                    </span>
                </button>

                {/* Config Wrapper */}
                {[
                    { title: 'Configuración', icon: Settings, href: '/configuracion' },
                ].map((action) => (
                    <Link
                        key={action.title}
                        href={action.href}
                        className="w-full flex items-center h-10 px-2.5 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100/50 dark:hover:bg-white/5 hover:text-gray-900 dark:hover:text-white transition-all duration-200 overflow-hidden"
                    >
                        <div className="shrink-0 w-5 h-5 flex items-center justify-center">
                            <action.icon className="w-[18px] h-[18px]" />
                        </div>
                        <span className={`ml-3 font-medium text-[13px] whitespace-nowrap overflow-hidden transition-all duration-300 ${isExpanded ? "opacity-100 max-w-[150px]" : "opacity-0 max-w-0"}`}>
                            {action.title}
                        </span>
                    </Link>
                ))}

                <div className={`mt-2 flex items-center gap-3 p-2 rounded-xl transition-all duration-300 overflow-hidden ${isExpanded ? "bg-gray-50 dark:bg-black/20" : "justify-center"}`}>
                    <div className="relative shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-[#2E66F6] to-[#1a4fd4] flex items-center justify-center text-white shadow-sm">
                        <User className="w-4 h-4" />
                        <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-500 border-2 border-white dark:border-[#263238] rounded-full" />
                    </div>

                    <div className={`flex flex-col whitespace-nowrap overflow-hidden transition-all duration-300 ${isExpanded ? "opacity-100 max-w-[120px]" : "opacity-0 max-w-0"}`}>
                        <span className="font-semibold text-[13px] text-gray-900 dark:text-white truncate leading-tight">Fabio Vallejo</span>
                        <span className="text-[10px] text-gray-500 dark:text-gray-400 truncate leading-tight">Admin</span>
                    </div>

                    <button
                        onClick={logout}
                        className={`ml-auto p-1.5 hover:cursor-pointer rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10 transition-all duration-200 ${isExpanded ? "opacity-100" : "opacity-0 w-0 hidden"}`}
                        title="Cerrar sesión"
                    >
                        <LogOut className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </aside>
    );
}
