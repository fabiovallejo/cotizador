"use client";

import { useState, useEffect, useCallback } from "react";
import {
    BarChart3, Calendar, Download, Loader2,
    Package, DollarSign, TrendingUp, Hash,
    AlertTriangle, XCircle, Info, Target,
} from "lucide-react";
import {
    obtenerReporteProductosTop,
    ReporteProductosTop,
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

export default function ReporteProductosTopPage() {
    const [fechaInicio, setFechaInicio] = useState(monthAgo);
    const [fechaFin, setFechaFin] = useState(today);
    const [data, setData] = useState<ReporteProductosTop | null>(null);
    const [loading, setLoading] = useState(false);

    const cargar = useCallback(async () => {
        setLoading(true);
        try {
            const r = await obtenerReporteProductosTop(fechaInicio, fechaFin);
            setData(r);
        } catch { }
        finally { setLoading(false); }
    }, [fechaInicio, fechaFin]);

    useEffect(() => { cargar(); }, [cargar]);

    const exportarExcel = () => {
        if (!data) return;
        const ws = XLSX.utils.json_to_sheet(data.productos.map((p, i) => ({
            "#": i + 1,
            "Código": p.codigo,
            "Producto": p.nombre,
            "Cantidad": p.cantidad_vendida,
            "Ingresos": p.ingresos,
            "% del Total": p.porcentaje_total,
            "Margen": p.margen ?? "N/A",
            "Tasa Conversión": `${p.tasa_conversion}%`,
            "Cot. Totales": p.total_cotizaciones,
            "Cot. Cerradas": p.cotizaciones_cerradas,
            "Monto Sin Cerrar": p.monto_no_cerrado,
        })));
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Productos Top");
        XLSX.writeFile(wb, `reporte_productos_top_${fechaInicio}_${fechaFin}.xlsx`);
    };

    const inputCls = "px-3 py-2 rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#2E66F6]/30 focus:border-[#2E66F6] outline-none transition";

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2.5">
                        <div className="p-2 rounded-xl bg-gradient-to-br from-[#FF7043] to-[#e64a19] shadow-lg shadow-orange-500/20">
                            <Package className="w-5 h-5 text-white" />
                        </div>
                        Productos Más Cotizados
                    </h1>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Ranking por ingresos con tasa de conversión y alertas</p>
                </div>
                <button onClick={exportarExcel} disabled={!data?.productos.length}
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
                <button onClick={cargar}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#2E66F6] hover:bg-[#2559d4] text-white text-sm font-medium transition shadow-lg shadow-blue-500/20">
                    <BarChart3 className="w-4 h-4" /> Generar
                </button>
            </div>

            {loading && (
                <div className="py-16 flex justify-center">
                    <Loader2 className="w-7 h-7 animate-spin text-[#FF7043]" />
                </div>
            )}

            {!loading && data && (
                <>
                    {/* Alertas */}
                    <AlertasPanel alertas={data.alertas} />

                    {/* Summary */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="relative overflow-hidden rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-5 shadow-sm">
                            <div className="absolute -top-4 -right-4 w-16 h-16 rounded-full bg-gradient-to-br from-[#FF7043] to-[#e64a19] opacity-10" />
                            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#FF7043] to-[#e64a19] flex items-center justify-center mb-3 shadow-lg">
                                <Hash className="w-4 h-4 text-white" />
                            </div>
                            <p className="text-xl font-bold text-gray-900 dark:text-white">{data.total_productos}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Productos cotizados</p>
                        </div>
                        <div className="relative overflow-hidden rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-5 shadow-sm">
                            <div className="absolute -top-4 -right-4 w-16 h-16 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-700 opacity-10" />
                            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-700 flex items-center justify-center mb-3 shadow-lg">
                                <DollarSign className="w-4 h-4 text-white" />
                            </div>
                            <p className="text-xl font-bold text-gray-900 dark:text-white">S/ {fmt(data.total_ingresos)}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Ingresos totales</p>
                        </div>
                        <div className="relative overflow-hidden rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 p-5 shadow-sm">
                            <div className="absolute -top-4 -right-4 w-16 h-16 rounded-full bg-gradient-to-br from-[#2E66F6] to-[#1a4fd4] opacity-10" />
                            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#2E66F6] to-[#1a4fd4] flex items-center justify-center mb-3 shadow-lg">
                                <TrendingUp className="w-4 h-4 text-white" />
                            </div>
                            <p className="text-xl font-bold text-gray-900 dark:text-white">
                                S/ {fmt(data.total_productos > 0 ? data.total_ingresos / data.total_productos : 0)}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Ingreso promedio / producto</p>
                        </div>
                    </div>

                    {/* Table */}
                    <div className="rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-100 dark:border-white/5 shadow-sm overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="bg-gray-50 dark:bg-white/[0.02] border-b border-gray-100 dark:border-white/5">
                                        <th className="text-center px-4 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider w-12">#</th>
                                        <th className="text-left px-5 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Producto</th>
                                        <th className="text-right px-4 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Cant.</th>
                                        <th className="text-right px-5 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Ingresos</th>
                                        <th className="text-right px-5 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">% Total</th>
                                        <th className="text-center px-4 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Conversión</th>
                                        <th className="text-right px-5 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Sin cerrar</th>
                                        <th className="text-right px-5 py-3.5 font-semibold text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">Margen</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-50 dark:divide-white/5">
                                    {data.productos.length === 0 ? (
                                        <tr><td colSpan={8} className="text-center py-12 text-gray-400">No hay productos en este período</td></tr>
                                    ) : data.productos.map((p, i) => (
                                        <tr key={p.id} className="hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors">
                                            <td className="px-4 py-3.5 text-center">
                                                {i < 3 ? (
                                                    <span className={`inline-flex w-6 h-6 rounded-full items-center justify-center text-xs font-bold text-white ${i === 0 ? "bg-amber-400" : i === 1 ? "bg-gray-400" : "bg-amber-700"}`}>
                                                        {i + 1}
                                                    </span>
                                                ) : (
                                                    <span className="text-gray-400">{i + 1}</span>
                                                )}
                                            </td>
                                            <td className="px-5 py-3.5">
                                                <p className="font-medium text-gray-900 dark:text-white">{p.nombre}</p>
                                                <p className="text-xs text-gray-400 font-mono">{p.codigo}</p>
                                            </td>
                                            <td className="px-4 py-3.5 text-right text-gray-700 dark:text-gray-300">{p.cantidad_vendida}</td>
                                            <td className="px-5 py-3.5 text-right font-semibold text-gray-900 dark:text-white">S/ {fmt(p.ingresos)}</td>
                                            <td className="px-5 py-3.5 text-right">
                                                <div className="flex items-center justify-end gap-2">
                                                    <div className="w-16 h-1.5 bg-gray-100 dark:bg-white/10 rounded-full overflow-hidden">
                                                        <div className="h-full bg-gradient-to-r from-[#FF7043] to-[#e64a19] rounded-full" style={{ width: `${Math.min(p.porcentaje_total, 100)}%` }} />
                                                    </div>
                                                    <span className="text-xs text-gray-500 dark:text-gray-400 w-10 text-right">{p.porcentaje_total}%</span>
                                                </div>
                                            </td>
                                            <td className="px-4 py-3.5 text-center">
                                                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-xs font-semibold ${p.tasa_conversion >= 70 ? "bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400" :
                                                        p.tasa_conversion >= 50 ? "bg-amber-50 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400" :
                                                            "bg-red-50 text-red-500 dark:bg-red-900/30 dark:text-red-400"
                                                    }`}>
                                                    <Target className="w-3 h-3" />
                                                    {p.tasa_conversion}%
                                                </span>
                                                <p className="text-[10px] text-gray-400 mt-0.5">{p.cotizaciones_cerradas}/{p.total_cotizaciones}</p>
                                            </td>
                                            <td className="px-5 py-3.5 text-right">
                                                {p.monto_no_cerrado > 0 ? (
                                                    <span className="text-red-500 dark:text-red-400 font-medium text-xs">S/ {fmt(p.monto_no_cerrado)}</span>
                                                ) : (
                                                    <span className="text-gray-300 dark:text-gray-600 text-xs">—</span>
                                                )}
                                            </td>
                                            <td className="px-5 py-3.5 text-right">
                                                {p.margen !== null ? (
                                                    <span className={`font-medium ${p.margen >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-500"}`}>
                                                        S/ {fmt(p.margen)}
                                                    </span>
                                                ) : (
                                                    <span className="text-gray-400 text-xs">Sin costo</span>
                                                )}
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
