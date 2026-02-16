"use client";

import { useState, useEffect, useCallback } from "react";
import {
    Calendar, Download, Loader2,
    Users, DollarSign, Star, BarChart3, TrendingUp,
    AlertTriangle, XCircle, Info, Clock, UserX,
} from "lucide-react";
import {
    obtenerReporteClientes,
    ReporteClientes,
    Alerta,
} from "@/services/reportes.service";
import * as XLSX from "xlsx";

/* ── Helpers ── */
const fmt = (n: number) => n.toLocaleString("es-PE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const today = () => new Date().toISOString().slice(0, 10);
const monthAgo = () => {
    const d = new Date();
    d.setMonth(d.getMonth() - 1);
    return d.toISOString().slice(0, 10);
};

const alertaStyles: Record<string, { bg: string; border: string; icon: typeof Info; iconColor: string }> = {
    info: { bg: "bg-blue-50 dark:bg-blue-900/20", border: "border-blue-200 dark:border-blue-800/40", icon: Info, iconColor: "text-blue-500" },
    warning: { bg: "bg-amber-50 dark:bg-amber-900/20", border: "border-amber-200 dark:border-amber-800/40", icon: AlertTriangle, iconColor: "text-amber-500" },
    danger: { bg: "bg-red-50 dark:bg-red-900/20", border: "border-red-200 dark:border-red-800/40", icon: XCircle, iconColor: "text-red-500" },
};

function AlertasPanel({ alertas }: { alertas: Alerta[] }) {
    if (!alertas.length) return null;
    return (
        <div className="space-y-2">
            {alertas.map((a, i) => {
                const s = alertaStyles[a.tipo] || alertaStyles.info;
                const Icon = s.icon;
                return (
                    <div key={i} className={`flex items-start gap-3 px-4 py-3 rounded-xl border ${s.bg} ${s.border}`}>
                        <Icon className={`w-4 h-4 mt-0.5 shrink-0 ${s.iconColor}`} />
                        <p className="text-sm text-gray-700 dark:text-gray-300">{a.mensaje}</p>
                    </div>
                );
            })}
        </div>
    );
}

export default function ReporteClientesPage() {
    const [fechaInicio, setFechaInicio] = useState(monthAgo);
    const [fechaFin, setFechaFin] = useState(today);
    const [filtroSegmento, setFiltroSegmento] = useState<"" | "VIP" | "Regular" | "Inactivo">("");
    const [data, setData] = useState<ReporteClientes | null>(null);
    const [loading, setLoading] = useState(false);

    const cargar = useCallback(async () => {
        setLoading(true);
        try {
            const r = await obtenerReporteClientes(fechaInicio, fechaFin);
            setData(r);
        } catch { }
        finally { setLoading(false); }
    }, [fechaInicio, fechaFin]);

    useEffect(() => { cargar(); }, [cargar]);

    const clientesFiltrados = data?.clientes.filter((c) => {
        if (!filtroSegmento) return true;
        if (filtroSegmento === "Inactivo") return c.es_inactivo;
        return c.segmento === filtroSegmento;
    }) ?? [];

    const exportarExcel = () => {
        if (!clientesFiltrados.length) return;
        const ws = XLSX.utils.json_to_sheet(clientesFiltrados.map((c) => ({
            "Razón Social": c.razon_social,
            "Documento": `${c.tipo_documento} ${c.numero_documento}`,
            "Cotizaciones": c.total_cotizaciones,
            "Aceptadas": c.aceptadas,
            "Monto Total": c.monto_total,
            "Ticket Promedio": c.ticket_promedio,
            "Última Cotización": c.ultima_cotizacion,
            "Segmento": c.segmento,
            "Días Inactivo": c.dias_inactivo ?? "—",
            "Monto Histórico": c.monto_historico,
        })));
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Clientes");
        XLSX.writeFile(wb, `reporte_clientes_${fechaInicio}_${fechaFin}.xlsx`);
    };

    const inputCls = "px-3 py-2 rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#2E66F6]/30 focus:border-[#2E66F6] outline-none transition";

    const vipCount = data?.clientes.filter((c) => c.segmento === "VIP").length ?? 0;
    const inactivosCount = data?.inactivos ?? 0;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2.5">
                        <div className="p-2 rounded-xl bg-gradient-to-br from-violet-500 to-violet-700 shadow-lg shadow-violet-500/20">
                            <Users className="w-5 h-5 text-white" />
                        </div>
                        Reporte de Clientes
                    </h1>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Segmentación, actividad y alertas de inactividad</p>
                </div>
                <button onClick={exportarExcel} disabled={!clientesFiltrados.length}
                    className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium transition disabled:opacity-50 shadow-lg shadow-emerald-500/20">
                    <Download className="w-4 h-4" /> Exportar Excel
                </button>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap items-end gap-3 p-4 rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 shadow-sm">
                <div>
                    <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">Desde</label>
                    <div className="relative">
                        <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input type="date" value={fechaInicio} onChange={(e) => setFechaInicio(e.target.value)}
                            className={`${inputCls} pl-9`} />
                    </div>
                </div>
                <div>
                    <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">Hasta</label>
                    <div className="relative">
                        <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input type="date" value={fechaFin} onChange={(e) => setFechaFin(e.target.value)}
                            className={`${inputCls} pl-9`} />
                    </div>
                </div>
                <div>
                    <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">Segmento</label>
                    <select value={filtroSegmento} onChange={(e) => setFiltroSegmento(e.target.value as any)}
                        className={inputCls}>
                        <option value="">Todos</option>
                        <option value="VIP">VIP</option>
                        <option value="Regular">Regular</option>
                        <option value="Inactivo">Inactivos (+30 días)</option>
                    </select>
                </div>
                <button onClick={cargar}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#2E66F6] hover:bg-[#2559d4] text-white text-sm font-medium transition shadow-lg shadow-blue-500/20">
                    <BarChart3 className="w-4 h-4" /> Generar
                </button>
            </div>

            {loading && (
                <div className="py-16 flex justify-center">
                    <Loader2 className="w-7 h-7 animate-spin text-violet-500" />
                </div>
            )}

            {!loading && data && (
                <>
                    {/* Alertas */}
                    <AlertasPanel alertas={data.alertas} />

                    {/* Summary */}
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                        <div className="relative overflow-hidden rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-5 shadow-sm">
                            <div className="absolute -top-4 -right-4 w-16 h-16 rounded-full bg-gradient-to-br from-violet-500 to-violet-700 opacity-10" />
                            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-violet-700 flex items-center justify-center mb-3 shadow-lg">
                                <Users className="w-4 h-4 text-white" />
                            </div>
                            <p className="text-xl font-bold text-gray-900 dark:text-white">{data.total_clientes}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Total clientes</p>
                        </div>
                        <div className="relative overflow-hidden rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-5 shadow-sm">
                            <div className="absolute -top-4 -right-4 w-16 h-16 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 opacity-10" />
                            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center mb-3 shadow-lg">
                                <Star className="w-4 h-4 text-white" />
                            </div>
                            <p className="text-xl font-bold text-gray-900 dark:text-white">{vipCount}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Clientes VIP</p>
                        </div>
                        <div className="relative overflow-hidden rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-5 shadow-sm">
                            <div className="absolute -top-4 -right-4 w-16 h-16 rounded-full bg-gradient-to-br from-red-500 to-red-700 opacity-10" />
                            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-red-500 to-red-700 flex items-center justify-center mb-3 shadow-lg">
                                <UserX className="w-4 h-4 text-white" />
                            </div>
                            <p className="text-xl font-bold text-gray-900 dark:text-white">{inactivosCount}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Inactivos (+30d)</p>
                        </div>
                        <div className="relative overflow-hidden rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-5 shadow-sm">
                            <div className="absolute -top-4 -right-4 w-16 h-16 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-700 opacity-10" />
                            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-700 flex items-center justify-center mb-3 shadow-lg">
                                <DollarSign className="w-4 h-4 text-white" />
                            </div>
                            <p className="text-xl font-bold text-gray-900 dark:text-white">S/ {fmt(data.promedio_global)}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Ticket promedio</p>
                        </div>
                        <div className="relative overflow-hidden rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-5 shadow-sm">
                            <div className="absolute -top-4 -right-4 w-16 h-16 rounded-full bg-gradient-to-br from-[#2E66F6] to-[#1a4fd4] opacity-10" />
                            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#2E66F6] to-[#1a4fd4] flex items-center justify-center mb-3 shadow-lg">
                                <TrendingUp className="w-4 h-4 text-white" />
                            </div>
                            <p className="text-xl font-bold text-gray-900 dark:text-white">S/ {fmt(data.umbral_vip)}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Umbral VIP</p>
                        </div>
                    </div>

                    {/* Table */}
                    <div className="rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 shadow-sm overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="bg-gray-50 dark:bg-white/[0.02] border-b border-gray-100 dark:border-white/5">
                                        <th className="text-left px-5 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Cliente</th>
                                        <th className="text-center px-4 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Cot.</th>
                                        <th className="text-center px-4 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Acep.</th>
                                        <th className="text-right px-5 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Monto</th>
                                        <th className="text-right px-5 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Historial</th>
                                        <th className="text-right px-5 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Ticket Prom.</th>
                                        <th className="text-center px-4 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Inactividad</th>
                                        <th className="text-center px-4 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Segmento</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-50 dark:divide-white/5">
                                    {clientesFiltrados.length === 0 ? (
                                        <tr><td colSpan={8} className="text-center py-12 text-gray-400">No hay clientes en este período</td></tr>
                                    ) : clientesFiltrados.map((c) => (
                                        <tr key={c.id} className={`hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors ${c.es_inactivo ? "bg-red-50/30 dark:bg-red-900/5" : ""}`}>
                                            <td className="px-5 py-3.5">
                                                <p className="font-medium text-gray-900 dark:text-white">{c.razon_social}</p>
                                                <p className="text-xs text-gray-400 font-mono">{c.tipo_documento} {c.numero_documento}</p>
                                            </td>
                                            <td className="px-4 py-3.5 text-center text-gray-700 dark:text-gray-300">{c.total_cotizaciones}</td>
                                            <td className="px-4 py-3.5 text-center">
                                                <span className="text-emerald-600 dark:text-emerald-400 font-medium">{c.aceptadas}</span>
                                            </td>
                                            <td className="px-5 py-3.5 text-right font-semibold text-gray-900 dark:text-white">S/ {fmt(c.monto_total)}</td>
                                            <td className="px-5 py-3.5 text-right text-gray-500 dark:text-gray-400 text-xs">S/ {fmt(c.monto_historico)}</td>
                                            <td className="px-5 py-3.5 text-right text-gray-700 dark:text-gray-300">S/ {fmt(c.ticket_promedio)}</td>
                                            <td className="px-4 py-3.5 text-center">
                                                {c.dias_inactivo !== null ? (
                                                    <span className={`inline-flex items-center gap-1 text-xs font-medium ${c.dias_inactivo > 30 ? "text-red-500 dark:text-red-400" :
                                                            c.dias_inactivo > 15 ? "text-amber-500 dark:text-amber-400" :
                                                                "text-gray-400"
                                                        }`}>
                                                        <Clock className="w-3 h-3" />
                                                        {c.dias_inactivo}d
                                                    </span>
                                                ) : (
                                                    <span className="text-gray-300 text-xs">—</span>
                                                )}
                                            </td>
                                            <td className="px-4 py-3.5 text-center">
                                                <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold ${c.segmento === "VIP"
                                                        ? "bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                                                        : "bg-gray-100 text-gray-600 dark:bg-gray-700/40 dark:text-gray-300"
                                                    }`}>
                                                    {c.segmento === "VIP" && <Star className="w-3 h-3" />}
                                                    {c.segmento}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
