"use client";

import { useState, useEffect, useCallback } from "react";
import {
    FileText, TrendingUp, TrendingDown, DollarSign, Target,
    AlertTriangle, Clock, Users, Package, Award,
    ArrowUpRight, ArrowDownRight, Bell, UserX,
    Loader2, ChevronDown, Send, CheckCircle2, XCircle,
} from "lucide-react";
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, Area, AreaChart,
} from "recharts";
import { obtenerDashboard, DashboardData } from "@/services/dashboard.service";
import { cambiarEstadoCotizacion } from "@/services/cotizaciones.service";
import Link from "next/link";

/* ── Helpers ── */
const fmt = (n: number) =>
    n.toLocaleString("es-PE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const fmtShort = (n: number) => {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
    return n.toFixed(0);
};

const PERIODOS = [
    { label: "Últimos 7 días", value: 7 },
    { label: "Últimos 30 días", value: 30 },
    { label: "Últimos 90 días", value: 90 },
];

/* ── Variation Badge ── */
function VariacionBadge({ valor, invertido = false }: { valor: number; invertido?: boolean }) {
    const isPositive = invertido ? valor <= 0 : valor >= 0;
    const Icon = valor >= 0 ? ArrowUpRight : ArrowDownRight;
    return (
        <span className={`inline-flex items-center gap-0.5 text-xs font-semibold px-1.5 py-0.5 rounded-md ${isPositive
            ? "text-emerald-600 bg-emerald-50 dark:text-emerald-400 dark:bg-emerald-900/30"
            : "text-red-500 bg-red-50 dark:text-red-400 dark:bg-red-900/30"
            }`}>
            <Icon className="w-3 h-3" />
            {Math.abs(valor)}%
        </span>
    );
}

/* ── Custom Chart Tooltip ── */
function ChartTooltip({ active, payload, label }: any) {
    if (!active || !payload?.length) return null;
    return (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 shadow-xl text-xs">
            <p className="text-gray-500 dark:text-gray-400 mb-1">{label}</p>
            {payload.map((p: any) => (
                <p key={p.dataKey} className="font-semibold" style={{ color: p.color }}>
                    {p.name}: {p.value}
                </p>
            ))}
        </div>
    );
}

export default function DashboardPage() {
    const [periodo, setPeriodo] = useState(30);
    const [monedaIngresos, setMonedaIngresos] = useState<"PEN" | "USD">("PEN");
    const [menuOpen, setMenuOpen] = useState(false);
    const [data, setData] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);

    const handleQuickEstado = async (id: number, estado: string) => {
        setActionLoadingId(id);
        try {
            await cambiarEstadoCotizacion(id, estado);
            await cargar();
        } catch (e) {
            console.error("Error cambiando estado:", e);
        } finally {
            setActionLoadingId(null);
        }
    };

    const cargar = useCallback(async () => {
        setLoading(true);
        try {
            const d = await obtenerDashboard(periodo);
            setData(d);
        } catch { }
        finally { setLoading(false); }
    }, [periodo]);

    useEffect(() => { cargar(); }, [cargar]);

    const periodoLabel = PERIODOS.find((p) => p.value === periodo)?.label ?? "";

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="text-center space-y-3">
                    <Loader2 className="w-8 h-8 animate-spin text-[#2E66F6] mx-auto" />
                    <p className="text-sm text-gray-500 dark:text-gray-400">Cargando dashboard...</p>
                </div>
            </div>
        );
    }

    if (!data) return null;

    const k = data.kpis;
    const convColor = k.tasa_conversion.valor >= 40
        ? "text-emerald-600 dark:text-emerald-400"
        : k.tasa_conversion.valor >= 20
            ? "text-amber-500 dark:text-amber-400"
            : "text-red-500 dark:text-red-400";

    return (
        <div className="space-y-6">
            {/* ═══════════════════════════════════════════════════════════════
                HEADER + PERÍODO
            ═══════════════════════════════════════════════════════════════ */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                        Dashboard
                    </h1>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                        Vista ejecutiva del estado de ventas
                    </p>
                </div>
                <div className="relative">
                    <button
                        onClick={() => setMenuOpen(!menuOpen)}
                        className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white dark:bg-white/[0.05] border border-gray-200 dark:border-white/10 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/10 transition shadow-sm"
                    >
                        <Clock className="w-4 h-4 text-gray-400" />
                        {periodoLabel}
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                    </button>
                    {menuOpen && (
                        <div className="absolute right-0 mt-1 w-48 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-xl z-50 overflow-hidden">
                            {PERIODOS.map((p) => (
                                <button
                                    key={p.value}
                                    onClick={() => { setPeriodo(p.value); setMenuOpen(false); }}
                                    className={`w-full text-left px-4 py-2.5 text-sm transition ${periodo === p.value
                                        ? "bg-[#2E66F6]/10 text-[#2E66F6] dark:text-[#FF7043] font-semibold"
                                        : "text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/5"
                                        }`}
                                >
                                    {p.label}
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* ═══════════════════════════════════════════════════════════════
                4 KPI CARDS
            ═══════════════════════════════════════════════════════════════ */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Cotizaciones */}
                <div className="relative overflow-hidden rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-5 shadow-sm hover:shadow-md transition-shadow">
                    <div className="absolute -top-6 -right-6 w-20 h-20 rounded-full bg-gradient-to-br from-[#2E66F6] to-[#1a4fd4] opacity-[0.08]" />
                    <div className="flex items-center justify-between mb-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#2E66F6] to-[#1a4fd4] flex items-center justify-center shadow-lg shadow-blue-500/20">
                            <FileText className="w-5 h-5 text-white" />
                        </div>
                        <VariacionBadge valor={k.cotizaciones.variacion} />
                    </div>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">{k.cotizaciones.valor}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Cotizaciones</p>
                </div>

                {/* Tasa conversión */}
                <div className="relative overflow-hidden rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-5 shadow-sm hover:shadow-md transition-shadow">
                    <div className="absolute -top-6 -right-6 w-20 h-20 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-700 opacity-[0.08]" />
                    <div className="flex items-center justify-between mb-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-700 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                            <Target className="w-5 h-5 text-white" />
                        </div>
                        <VariacionBadge valor={k.tasa_conversion.variacion} />
                    </div>
                    <p className={`text-3xl font-bold ${convColor}`}>{k.tasa_conversion.valor}%</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Conversión · {k.tasa_conversion.aceptadas}/{k.tasa_conversion.total}
                    </p>
                </div>

                {/* Ingresos */}
                <div className="relative overflow-hidden rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-4 sm:p-5 shadow-sm hover:shadow-md transition-shadow">
                    <div className="absolute -top-6 -right-6 w-20 h-20 rounded-full bg-gradient-to-br from-[#FF7043] to-[#e64a19] opacity-[0.08]" />
                    <div className="flex items-start justify-between mb-3 relative z-10">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#FF7043] to-[#e64a19] flex items-center justify-center shadow-lg shadow-orange-500/20 shrink-0">
                            <DollarSign className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex flex-col items-end gap-2">
                            <VariacionBadge valor={monedaIngresos === "PEN" ? k.ingresos_pen.variacion : k.ingresos_usd.variacion} />
                            <div className="flex items-center bg-gray-100 dark:bg-white/10 rounded-lg p-0.5">
                                <button onClick={() => setMonedaIngresos("PEN")} className={`px-2 py-0.5 text-[10px] font-bold rounded-md transition-colors ${monedaIngresos === "PEN" ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm" : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"}`}>PEN</button>
                                <button onClick={() => setMonedaIngresos("USD")} className={`px-2 py-0.5 text-[10px] font-bold rounded-md transition-colors ${monedaIngresos === "USD" ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm" : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"}`}>USD</button>
                            </div>
                        </div>
                    </div>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white relative z-10 transition-all">
                        {monedaIngresos === "PEN" ? "S/ " : "$ "}{fmtShort(monedaIngresos === "PEN" ? k.ingresos_pen.valor : k.ingresos_usd.valor)}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 relative z-10">
                        Ingresos · Prom. {monedaIngresos === "PEN" ? "S/ " : "$ "}{fmt(monedaIngresos === "PEN" ? k.ingresos_pen.ticket_promedio : k.ingresos_usd.ticket_promedio)}
                    </p>
                </div>

                {/* Alertas */}
                <div className="relative overflow-hidden rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-5 shadow-sm hover:shadow-md transition-shadow">
                    <div className="absolute -top-6 -right-6 w-20 h-20 rounded-full bg-gradient-to-br from-red-500 to-red-700 opacity-[0.08]" />
                    <div className="flex items-center justify-between mb-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-red-500 to-red-700 flex items-center justify-center shadow-lg shadow-red-500/20">
                            <Bell className="w-5 h-5 text-white" />
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="text-center">
                            <p className="text-2xl font-bold text-red-500">{k.alertas.pendientes}</p>
                            <p className="text-[10px] text-gray-400">Pendientes</p>
                        </div>
                        <div className="w-px h-8 bg-gray-200 dark:bg-white/10" />
                        <div className="text-center">
                            <p className="text-2xl font-bold text-[#FF7043]">{k.alertas.inactivos}</p>
                            <p className="text-[10px] text-gray-400">Inactivos</p>
                        </div>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Requieren atención</p>
                </div>
            </div>

            {/* ═══════════════════════════════════════════════════════════════
                ALERTA CRÍTICA — COTIZACIONES PENDIENTES
            ═══════════════════════════════════════════════════════════════ */}
            {data.cotizaciones_pendientes.length > 0 && (
                <div className="rounded-2xl border border-red-200 dark:border-red-800/30 bg-red-50/50 dark:bg-red-900/10 overflow-hidden">
                    <div className="px-5 py-3 bg-red-100/60 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800/30 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 text-red-500" />
                        <span className="text-sm font-semibold text-red-700 dark:text-red-400">
                            {data.cotizaciones_pendientes.length} cotización(es) sin respuesta — Hacer seguimiento
                        </span>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-red-100 dark:border-red-900/20">
                                    <th className="text-left px-5 py-2.5 text-xs font-medium text-red-500/70 uppercase tracking-wider">Cliente</th>
                                    <th className="text-left px-4 py-2.5 text-xs font-medium text-red-500/70 uppercase tracking-wider">Fecha</th>
                                    <th className="text-center px-4 py-2.5 text-xs font-medium text-red-500/70 uppercase tracking-wider">Días</th>
                                    <th className="text-right px-5 py-2.5 text-xs font-medium text-red-500/70 uppercase tracking-wider">Monto</th>
                                    <th className="text-left px-4 py-2.5 text-xs font-medium text-red-500/70 uppercase tracking-wider">Vendedor</th>
                                    <th className="text-center px-4 py-2.5 text-xs font-medium text-red-500/70 uppercase tracking-wider">Acción</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-red-100 dark:divide-red-900/20">
                                {data.cotizaciones_pendientes.map((p) => (
                                    <tr key={p.id} className="hover:bg-red-100/30 dark:hover:bg-red-900/10 transition-colors">
                                        <td className="px-5 py-2.5">
                                            <Link href={`/dashboard/cotizaciones`}
                                                className="font-medium text-red-700 dark:text-red-400 hover:underline">
                                                {p.cliente}
                                            </Link>
                                            <p className="text-[11px] text-red-400/70 dark:text-red-500/60">{p.numero}</p>
                                        </td>
                                        <td className="px-4 py-2.5 text-gray-600 dark:text-gray-400">{p.fecha}</td>
                                        <td className="px-4 py-2.5 text-center">
                                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 text-xs font-bold">
                                                <Clock className="w-3 h-3" />
                                                {p.dias}d
                                            </span>
                                        </td>
                                        <td className="px-5 py-2.5 text-right font-semibold text-gray-900 dark:text-white">S/ {fmt(p.monto)}</td>
                                        <td className="px-4 py-2.5 text-gray-500 dark:text-gray-400">{p.vendedor}</td>
                                        <td className="px-4 py-2.5 text-center">
                                            {actionLoadingId === p.id ? (
                                                <Loader2 className="w-4 h-4 animate-spin text-blue-500 mx-auto" />
                                            ) : p.estado === "borrador" ? (
                                                <button
                                                    onClick={() => handleQuickEstado(p.id, "enviada")}
                                                    className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 dark:text-blue-400 dark:bg-blue-900/20 dark:hover:bg-blue-900/40 transition-colors"
                                                    title="Marcar como enviada"
                                                >
                                                    <Send className="w-3 h-3" />
                                                    Enviada
                                                </button>
                                            ) : (
                                                <span className="inline-flex items-center gap-1 text-[11px] text-amber-600 dark:text-amber-400">
                                                    <Clock className="w-3 h-3" />
                                                    Esperando
                                                </span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* ═══════════════════════════════════════════════════════════════
                GRÁFICO + TOP 5 PRODUCTOS (side by side)
            ═══════════════════════════════════════════════════════════════ */}
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
                {/* Gráfico — 3 cols */}
                <div className="lg:col-span-3 rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-5 shadow-sm">
                    <h2 className="text-sm font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-[#2E66F6]" />
                        Evolución de Cotizaciones
                    </h2>
                    <div className="h-[280px]">
                        {data.serie_diaria.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={data.serie_diaria} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
                                    <defs>
                                        <linearGradient id="gradTotal" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#2E66F6" stopOpacity={0.2} />
                                            <stop offset="100%" stopColor="#2E66F6" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="gradAcep" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#10b981" stopOpacity={0.2} />
                                            <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(128,128,128,0.1)" />
                                    <XAxis
                                        dataKey="dia"
                                        tick={{ fontSize: 11, fill: "#9ca3af" }}
                                        tickFormatter={(v: string) => {
                                            const d = new Date(v + "T00:00:00");
                                            return `${d.getDate()}/${d.getMonth() + 1}`;
                                        }}
                                        axisLine={false}
                                        tickLine={false}
                                    />
                                    <YAxis
                                        tick={{ fontSize: 11, fill: "#9ca3af" }}
                                        axisLine={false}
                                        tickLine={false}
                                        allowDecimals={false}
                                    />
                                    <Tooltip content={<ChartTooltip />} />
                                    <Area type="monotone" dataKey="total" name="Total" stroke="#2E66F6" strokeWidth={2.5} fill="url(#gradTotal)" dot={false} activeDot={{ r: 5, strokeWidth: 2 }} />
                                    <Area type="monotone" dataKey="aceptadas" name="Aceptadas" stroke="#10b981" strokeWidth={2} fill="url(#gradAcep)" dot={false} activeDot={{ r: 4, strokeWidth: 2 }} />
                                </AreaChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex items-center justify-center h-full text-gray-400 text-sm">
                                Sin datos para este período
                            </div>
                        )}
                    </div>
                    <div className="flex items-center gap-5 mt-3 pt-3 border-t border-gray-100 dark:border-white/5">
                        <div className="flex items-center gap-1.5 text-xs text-gray-500">
                            <div className="w-3 h-0.5 rounded-full bg-[#2E66F6]" />
                            Total
                        </div>
                        <div className="flex items-center gap-1.5 text-xs text-gray-500">
                            <div className="w-3 h-0.5 rounded-full bg-emerald-500" />
                            Aceptadas
                        </div>
                    </div>
                </div>

                {/* Top 5 Productos — 2 cols */}
                <div className="lg:col-span-2 rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-5 shadow-sm">
                    <h2 className="text-sm font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                        <Package className="w-4 h-4 text-[#FF7043]" />
                        Top 5 Productos
                    </h2>
                    {data.top_productos.length === 0 ? (
                        <p className="text-sm text-gray-400 text-center py-8">Sin datos</p>
                    ) : (
                        <div className="space-y-2">
                            {data.top_productos.map((p, i) => (
                                <Link href="/dashboard/reportes/productos-top" key={p.id}
                                    className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-colors ${p.tasa_conversion < 30
                                        ? "bg-amber-50/50 dark:bg-amber-900/10 hover:bg-amber-50 dark:hover:bg-amber-900/20"
                                        : "hover:bg-gray-50 dark:hover:bg-white/[0.03]"
                                        }`}
                                >
                                    <span className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold text-white shrink-0 ${i === 0 ? "bg-amber-400" : i === 1 ? "bg-gray-400" : i === 2 ? "bg-amber-700" : "bg-gray-300 dark:bg-gray-600"
                                        }`}>
                                        {i + 1}
                                    </span>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                            {p.tasa_conversion < 30 && <span className="text-amber-500 mr-1">⚠️</span>}
                                            {p.nombre}
                                        </p>
                                        <p className="text-[11px] text-gray-400">
                                            {p.cantidad} uds · Conv. {p.tasa_conversion}%
                                        </p>
                                    </div>
                                    <div className="text-right shrink-0">
                                        <p className="text-sm font-semibold text-gray-900 dark:text-white">
                                            S/ {fmtShort(p.ingresos)}
                                        </p>
                                        <p className={`text-[11px] font-medium ${p.tasa_conversion >= 60 ? "text-emerald-500" :
                                            p.tasa_conversion >= 30 ? "text-gray-400" :
                                                "text-amber-500"
                                            }`}>
                                            {p.tasa_conversion}%
                                        </p>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* ═══════════════════════════════════════════════════════════════
                PRODUCTOS PROBLEMÁTICOS
            ═══════════════════════════════════════════════════════════════ */}
            {data.productos_problematicos.length > 0 && (
                <div className="rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 shadow-sm overflow-hidden">
                    <div className="px-5 py-3.5 border-b border-gray-100 dark:border-white/5 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 text-amber-500" />
                        <h2 className="text-sm font-semibold text-gray-900 dark:text-white">
                            Productos con Baja Conversión
                        </h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="bg-gray-50/50 dark:bg-white/[0.01] border-b border-gray-100 dark:border-white/5">
                                    <th className="text-left px-5 py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Producto</th>
                                    <th className="text-center px-4 py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Cotizadas</th>
                                    <th className="text-center px-4 py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Cerradas</th>
                                    <th className="text-center px-4 py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Conv %</th>
                                    <th className="text-right px-5 py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Monto perdido</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-50 dark:divide-white/5">
                                {data.productos_problematicos.map((p) => (
                                    <tr key={p.id} className="hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors">
                                        <td className="px-5 py-3">
                                            <p className="font-medium text-gray-900 dark:text-white">{p.nombre}</p>
                                            <p className="text-[11px] text-gray-400 font-mono">{p.codigo}</p>
                                        </td>
                                        <td className="px-4 py-3 text-center text-gray-700 dark:text-gray-300">{p.cotizaciones_total}</td>
                                        <td className="px-4 py-3 text-center text-emerald-600 dark:text-emerald-400 font-medium">{p.cotizaciones_cerradas}</td>
                                        <td className="px-4 py-3 text-center">
                                            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-bold ${p.tasa_conversion < 30
                                                ? "bg-red-50 text-red-500 dark:bg-red-900/30 dark:text-red-400"
                                                : "bg-amber-50 text-amber-500 dark:bg-amber-900/30 dark:text-amber-400"
                                                }`}>
                                                {p.tasa_conversion}%
                                            </span>
                                        </td>
                                        <td className="px-5 py-3 text-right font-semibold text-red-500 dark:text-red-400">
                                            S/ {fmt(p.monto_perdido)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* ═══════════════════════════════════════════════════════════════
                CLIENTES INACTIVOS + TOP VENDEDORES (side by side)
            ═══════════════════════════════════════════════════════════════ */}
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
                {/* Clientes Inactivos — 3 cols */}
                <div className="lg:col-span-3 rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 shadow-sm overflow-hidden">
                    <div className="px-5 py-3.5 border-b border-gray-100 dark:border-white/5 flex items-center gap-2">
                        <UserX className="w-4 h-4 text-red-500" />
                        <h2 className="text-sm font-semibold text-gray-900 dark:text-white">
                            Clientes Inactivos (30+ días)
                        </h2>
                    </div>
                    {data.clientes_inactivos.length === 0 ? (
                        <div className="px-5 py-8 text-center text-gray-400 text-sm">
                            🎉 Sin clientes inactivos
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="bg-gray-50/50 dark:bg-white/[0.01] border-b border-gray-100 dark:border-white/5">
                                        <th className="text-left px-5 py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Cliente</th>
                                        <th className="text-left px-4 py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Última cot.</th>
                                        <th className="text-center px-4 py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Días</th>
                                        <th className="text-right px-5 py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Historial</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-50 dark:divide-white/5">
                                    {data.clientes_inactivos.map((c) => (
                                        <tr key={c.id} className="hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors">
                                            <td className="px-5 py-3 font-medium text-gray-900 dark:text-white">{c.razon_social}</td>
                                            <td className="px-4 py-3 text-gray-500 dark:text-gray-400">{c.ultima_cotizacion}</td>
                                            <td className="px-4 py-3 text-center">
                                                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-bold ${c.dias > 60
                                                    ? "bg-red-50 text-red-500 dark:bg-red-900/30 dark:text-red-400"
                                                    : "bg-amber-50 text-amber-500 dark:bg-amber-900/30 dark:text-amber-400"
                                                    }`}>
                                                    <Clock className="w-3 h-3" />
                                                    {c.dias}d
                                                </span>
                                            </td>
                                            <td className="px-5 py-3 text-right text-gray-700 dark:text-gray-300">S/ {fmt(c.monto_historico)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                {/* Top Vendedores — 2 cols */}
                <div className="lg:col-span-2 rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-5 shadow-sm">
                    <h2 className="text-sm font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                        <Award className="w-4 h-4 text-amber-500" />
                        Top Vendedores
                    </h2>
                    {data.top_vendedores.length === 0 ? (
                        <p className="text-sm text-gray-400 text-center py-8">Sin datos</p>
                    ) : (
                        <div className="space-y-2.5">
                            {data.top_vendedores.map((v, i) => {
                                const medals = ["🥇", "🥈", "🥉"];
                                const barWidth = Math.min(v.tasa_conversion, 100);
                                return (
                                    <div key={v.id} className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-gray-50 dark:hover:bg-white/[0.03] transition-colors">
                                        <span className="text-lg shrink-0 w-6 text-center">
                                            {i < 3 ? medals[i] : <span className="text-xs text-gray-400">{i + 1}</span>}
                                        </span>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{v.nombre}</p>
                                            <div className="flex items-center gap-2 mt-1">
                                                <div className="flex-1 h-1.5 bg-gray-100 dark:bg-white/10 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full transition-all ${i === 0
                                                            ? "bg-gradient-to-r from-amber-400 to-amber-500"
                                                            : "bg-gradient-to-r from-[#2E66F6] to-[#1a4fd4]"
                                                            }`}
                                                        style={{ width: `${barWidth}%` }}
                                                    />
                                                </div>
                                                <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 w-10 text-right">
                                                    {v.tasa_conversion}%
                                                </span>
                                            </div>
                                        </div>
                                        <div className="text-right shrink-0">
                                            <p className="text-xs text-gray-400">
                                                {v.cerradas}/{v.cotizaciones}
                                            </p>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
