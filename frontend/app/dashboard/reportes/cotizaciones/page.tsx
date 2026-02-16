"use client";

import { useState, useEffect, useCallback } from "react";
import {
    BarChart3, Calendar, Download, Filter, Loader2,
    FileText, TrendingUp, Percent, Target, DollarSign,
    AlertTriangle, Clock, XCircle, Info,
} from "lucide-react";
import {
    obtenerReporteCotizaciones,
    ReporteCotizaciones,
    Alerta,
} from "@/services/reportes.service";
import { listarUsuarios } from "@/services/configuracion.service";
import * as XLSX from "xlsx";

/* ── Helpers ── */
const fmt = (n: number) => n.toLocaleString("es-PE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const today = () => new Date().toISOString().slice(0, 10);
const monthAgo = () => {
    const d = new Date();
    d.setMonth(d.getMonth() - 1);
    return d.toISOString().slice(0, 10);
};

const estadoColor: Record<string, string> = {
    borrador: "bg-gray-100 text-gray-600 dark:bg-gray-700/40 dark:text-gray-300",
    enviada: "bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
    aceptada: "bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400",
    rechazada: "bg-red-50 text-red-500 dark:bg-red-900/30 dark:text-red-400",
    vencida: "bg-amber-50 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400",
    convertida: "bg-violet-50 text-violet-600 dark:bg-violet-900/30 dark:text-violet-400",
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

export default function ReporteCotizacionesPage() {
    const [fechaInicio, setFechaInicio] = useState(monthAgo);
    const [fechaFin, setFechaFin] = useState(today);
    const [vendedorId, setVendedorId] = useState<number | undefined>();
    const [data, setData] = useState<ReporteCotizaciones | null>(null);
    const [loading, setLoading] = useState(false);
    const [vendedores, setVendedores] = useState<{ id: number; nombre: string }[]>([]);

    useEffect(() => {
        listarUsuarios().then((u) =>
            setVendedores(u.map((v: any) => ({ id: v.id, nombre: `${v.nombre} ${v.apellido || ""}`.trim() })))
        ).catch(() => { });
    }, []);

    const cargar = useCallback(async () => {
        setLoading(true);
        try {
            const r = await obtenerReporteCotizaciones(fechaInicio, fechaFin, vendedorId);
            setData(r);
        } catch { }
        finally { setLoading(false); }
    }, [fechaInicio, fechaFin, vendedorId]);

    useEffect(() => { cargar(); }, [cargar]);

    const exportarExcel = () => {
        if (!data) return;
        const ws = XLSX.utils.json_to_sheet(data.detalle.map((d) => ({
            "Número": d.numero,
            "Cliente": d.cliente,
            "Vendedor": d.vendedor,
            "Total": d.total,
            "Moneda": d.moneda,
            "Estado": d.estado,
            "Fecha": d.fecha,
        })));
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Cotizaciones");
        XLSX.writeFile(wb, `reporte_cotizaciones_${fechaInicio}_${fechaFin}.xlsx`);
    };

    const inputCls = "px-3 py-2 rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#2E66F6]/30 focus:border-[#2E66F6] outline-none transition";

    const m = data?.metricas;

    const kpis = m ? [
        { label: "Total cotizaciones", value: m.total_cotizaciones, icon: FileText, color: "from-[#2E66F6] to-[#1a4fd4]" },
        { label: "Monto total", value: `S/ ${fmt(m.monto_total)}`, icon: DollarSign, color: "from-emerald-500 to-emerald-700" },
        { label: "% Aceptadas", value: `${m.porcentaje_aceptadas}%`, icon: Percent, color: "from-[#FF7043] to-[#e64a19]" },
        { label: "Tasa conversión", value: `${m.tasa_conversion}%`, icon: Target, color: "from-violet-500 to-violet-700" },
        { label: "Valor promedio", value: `S/ ${fmt(m.valor_promedio)}`, icon: TrendingUp, color: "from-amber-500 to-amber-700" },
        { label: "Tasa rechazo", value: `${m.tasa_rechazo}%`, icon: XCircle, color: m.tasa_rechazo > 30 ? "from-red-500 to-red-700" : "from-gray-400 to-gray-600" },
        { label: "Pendientes (+7 días)", value: m.pendientes, icon: Clock, color: m.pendientes > 0 ? "from-amber-500 to-amber-700" : "from-gray-400 to-gray-600" },
        { label: "Monto en riesgo", value: `S/ ${fmt(m.monto_perdido)}`, icon: AlertTriangle, color: m.monto_perdido > 0 ? "from-red-500 to-red-700" : "from-gray-400 to-gray-600" },
    ] : [];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2.5">
                        <div className="p-2 rounded-xl bg-gradient-to-br from-[#2E66F6] to-[#1a4fd4] shadow-lg shadow-blue-500/20">
                            <BarChart3 className="w-5 h-5 text-white" />
                        </div>
                        Reporte de Cotizaciones
                    </h1>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Análisis de rendimiento, conversión y alertas de seguimiento</p>
                </div>
                <button onClick={exportarExcel} disabled={!data?.detalle.length}
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
                    <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">Vendedor</label>
                    <select value={vendedorId ?? ""} onChange={(e) => setVendedorId(e.target.value ? Number(e.target.value) : undefined)}
                        className={inputCls}>
                        <option value="">Todos</option>
                        {vendedores.map((v) => <option key={v.id} value={v.id}>{v.nombre}</option>)}
                    </select>
                </div>
                <button onClick={cargar}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#2E66F6] hover:bg-[#2559d4] text-white text-sm font-medium transition shadow-lg shadow-blue-500/20">
                    <Filter className="w-4 h-4" /> Filtrar
                </button>
            </div>

            {loading && (
                <div className="py-16 flex justify-center">
                    <Loader2 className="w-7 h-7 animate-spin text-[#2E66F6]" />
                </div>
            )}

            {!loading && data && (
                <>
                    {/* Alertas */}
                    <AlertasPanel alertas={data.alertas} />

                    {/* KPI Cards */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {kpis.map((kpi) => (
                            <div key={kpi.label}
                                className="relative overflow-hidden rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-5 shadow-sm hover:shadow-md transition-shadow">
                                <div className={`absolute -top-4 -right-4 w-16 h-16 rounded-full bg-gradient-to-br ${kpi.color} opacity-10`} />
                                <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${kpi.color} flex items-center justify-center mb-3 shadow-lg`}>
                                    <kpi.icon className="w-4 h-4 text-white" />
                                </div>
                                <p className="text-xl font-bold text-gray-900 dark:text-white">{kpi.value}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{kpi.label}</p>
                            </div>
                        ))}
                    </div>

                    {/* Table */}
                    <div className="rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 shadow-sm overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="bg-gray-50 dark:bg-white/[0.02] border-b border-gray-100 dark:border-white/5">
                                        <th className="text-left px-5 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">N°</th>
                                        <th className="text-left px-5 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Cliente</th>
                                        <th className="text-left px-5 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Vendedor</th>
                                        <th className="text-right px-5 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Total</th>
                                        <th className="text-center px-5 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Estado</th>
                                        <th className="text-left px-5 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Fecha</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-50 dark:divide-white/5">
                                    {data.detalle.length === 0 ? (
                                        <tr><td colSpan={6} className="text-center py-12 text-gray-400">No hay cotizaciones en este período</td></tr>
                                    ) : data.detalle.map((d) => (
                                        <tr key={d.id} className="hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors">
                                            <td className="px-5 py-3.5 font-medium text-[#2E66F6] dark:text-[#FF7043]">{d.numero}</td>
                                            <td className="px-5 py-3.5 text-gray-700 dark:text-gray-300">{d.cliente}</td>
                                            <td className="px-5 py-3.5 text-gray-500 dark:text-gray-400">{d.vendedor}</td>
                                            <td className="px-5 py-3.5 text-right font-semibold text-gray-900 dark:text-white">S/ {fmt(d.total)}</td>
                                            <td className="px-5 py-3.5 text-center">
                                                <span className={`inline-flex px-2.5 py-1 rounded-lg text-xs font-semibold ${estadoColor[d.estado] || "bg-gray-100 text-gray-600"}`}>
                                                    {d.estado}
                                                </span>
                                            </td>
                                            <td className="px-5 py-3.5 text-gray-500 dark:text-gray-400">{d.fecha}</td>
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
