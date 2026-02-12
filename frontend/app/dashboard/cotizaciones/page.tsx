"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import {
    listarCotizaciones,
    eliminarCotizacion,
    descargarPdfCotizacion,
} from "@/services/cotizaciones.service";
import { listarClientes } from "@/services/clientes.service";
import { apiFetch } from "@/lib/api";
import type { Cotizacion } from "@/types/cotizaciones";
import type { Cliente } from "@/types/clientes";
import {
    Plus,
    Pencil,
    Trash2,
    FileDown,
    FileText,
    CalendarDays,
    Search,
    X,
    Filter,
    Users,
    Loader2,
} from "lucide-react";
import Link from "next/link";

import { clsx } from "clsx";

/* ── User type (minimal) ── */
interface Usuario {
    id: number;
    nombre: string;
    apellido?: string;
    rol: string;
}

/* ── Estado → color mapping ── */
const estadoConfig: Record<string, { label: string; classes: string }> = {
    borrador: {
        label: "Borrador",
        classes:
            "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400",
    },
    enviada: {
        label: "Enviada",
        classes:
            "bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
    },
    aceptada: {
        label: "Aceptada",
        classes:
            "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
    },
    rechazada: {
        label: "Rechazada",
        classes:
            "bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400",
    },
    convertida: {
        label: "Convertida",
        classes:
            "bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
    },
    vencida: {
        label: "Vencida",
        classes:
            "bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
    },
};

const formatCurrency = (value: number, moneda: string) => {
    const symbol = moneda === "USD" ? "$" : "S/";
    return `${symbol} ${Number(value).toFixed(2)}`;
};

const formatDate = (dateStr?: string) => {
    if (!dateStr) return "—";
    const d = new Date(dateStr);
    return d.toLocaleDateString("es-PE", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    });
};

export default function CotizacionesPage() {
    const [cotizaciones, setCotizaciones] = useState<Cotizacion[]>([]);
    const [clientes, setClientes] = useState<Cliente[]>([]);
    const [usuarios, setUsuarios] = useState<Usuario[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [deletingCotizacion, setDeletingCotizacion] =
        useState<Cotizacion | null>(null);

    /* ── Filter state ── */
    const [searchTerm, setSearchTerm] = useState("");
    const [estadoFilter, setEstadoFilter] = useState<string>("");
    const [vendedorFilter, setVendedorFilter] = useState<number | "">("");

    /* ── Fetch data ── */
    const fetchCotizaciones = useCallback(async () => {
        setIsLoading(true);
        try {
            const params: { busqueda?: string; estado?: string; usuario_id?: number } = {};
            if (searchTerm.trim()) params.busqueda = searchTerm.trim();
            if (estadoFilter) params.estado = estadoFilter;
            if (vendedorFilter) params.usuario_id = vendedorFilter as number;
            const data = await listarCotizaciones(params);
            setCotizaciones(data);
        } catch (error) {
            console.error("Error fetching cotizaciones:", error);
        } finally {
            setIsLoading(false);
        }
    }, [searchTerm, estadoFilter, vendedorFilter]);

    /* Initial load: clients + users + cotizaciones */
    useEffect(() => {
        const loadBaseData = async () => {
            try {
                const [cliData, usrData] = await Promise.all([
                    listarClientes(),
                    apiFetch<Usuario[]>("/utils/vendedores"),
                ]);
                setClientes(cliData);
                setUsuarios(usrData);
            } catch (error) {
                console.error("Error loading base data:", error);
            }
        };
        loadBaseData();
    }, []);

    /* Refetch cotizaciones when filters change (debounced for search) */
    useEffect(() => {
        const timer = setTimeout(() => {
            fetchCotizaciones();
        }, searchTerm ? 400 : 0);
        return () => clearTimeout(timer);
    }, [fetchCotizaciones, searchTerm]);

    /* Client lookup map */
    const clienteMap = useMemo(() => {
        const m = new Map<number, string>();
        clientes.forEach((c) => m.set(c.id, c.razon_social));
        return m;
    }, [clientes]);

    /* Vendor lookup map */
    const vendedorMap = useMemo(() => {
        const m = new Map<number, string>();
        usuarios.forEach((u) =>
            m.set(u.id, `${u.nombre}${u.apellido ? " " + u.apellido : ""}`)
        );
        return m;
    }, [usuarios]);

    const handleEliminar = async () => {
        if (!deletingCotizacion) return;
        try {
            await eliminarCotizacion(deletingCotizacion.id);
            setCotizaciones((prev) =>
                prev.filter((c) => c.id !== deletingCotizacion.id)
            );
        } catch (error) {
            console.error("Error deleting cotizacion:", error);
            throw error;
        }
    };

    const handleDescargarPdf = async (id: number) => {
        try {
            await descargarPdfCotizacion(id);
        } catch (error) {
            console.error("Error downloading PDF:", error);
        }
    };

    const clearFilters = () => {
        setSearchTerm("");
        setEstadoFilter("");
        setVendedorFilter("");
    };

    const hasActiveFilters = searchTerm || estadoFilter || vendedorFilter;

    return (
        <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
                        Cotizaciones{" "}
                        <span className="text-s text-gray-500 dark:text-gray-400">
                            ({cotizaciones.length})
                        </span>
                    </h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-1">
                        Gestiona tus cotizaciones y propuestas comerciales.
                    </p>
                </div>
                <Link
                    href="/dashboard/cotizaciones/nueva"
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-orange-600 px-4 py-2 text-sm font-medium text-white shadow-lg shadow-orange-500/20 hover:bg-orange-700 hover:shadow-orange-500/30 transition-all focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
                >
                    <Plus className="h-4 w-4" />
                    Nueva Cotización
                </Link>
            </div>

            {/* ── Filter Bar ── */}
            <div className="rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/50 shadow-sm p-4 space-y-3">
                {/* Row 1: Search */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Buscar por número de cotización, nombre de cliente o documento..."
                        className="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 pl-10 pr-10 py-2.5 text-sm outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all"
                    />
                    {searchTerm && (
                        <button
                            onClick={() => setSearchTerm("")}
                            className="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                        >
                            <X className="h-3.5 w-3.5" />
                        </button>
                    )}
                </div>

                {/* Row 2: Estado pills + Vendor dropdown */}
                <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                    {/* Estado filter pills */}
                    <div className="flex items-center gap-2 flex-wrap flex-1">
                        <Filter className="h-4 w-4 text-gray-400 shrink-0" />
                        <button
                            onClick={() => setEstadoFilter("")}
                            className={clsx(
                                "px-3 py-1.5 rounded-full text-xs font-medium transition-all",
                                !estadoFilter
                                    ? "bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900"
                                    : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700"
                            )}
                        >
                            Todos
                        </button>
                        {Object.entries(estadoConfig).map(([key, cfg]) => (
                            <button
                                key={key}
                                onClick={() =>
                                    setEstadoFilter(
                                        estadoFilter === key ? "" : key
                                    )
                                }
                                className={clsx(
                                    "px-3 py-1.5 rounded-full text-xs font-medium transition-all",
                                    estadoFilter === key
                                        ? cfg.classes +
                                        " ring-2 ring-offset-1 ring-current dark:ring-offset-gray-900"
                                        : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700"
                                )}
                            >
                                {cfg.label}
                            </button>
                        ))}
                    </div>

                    {/* Vendor filter dropdown */}
                    <div className="flex items-center gap-2 shrink-0">
                        <Users className="h-4 w-4 text-gray-400" />
                        <select
                            value={vendedorFilter}
                            onChange={(e) =>
                                setVendedorFilter(
                                    e.target.value
                                        ? Number(e.target.value)
                                        : ""
                                )
                            }
                            className="rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 px-3 py-1.5 text-xs outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all min-w-[160px]"
                        >
                            <option value="">Todos los vendedores</option>
                            {usuarios.map((u) => (
                                <option key={u.id} value={u.id}>
                                    {u.nombre}
                                    {u.apellido ? ` ${u.apellido}` : ""} (
                                    {u.rol})
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Clear filters */}
                    {hasActiveFilters && (
                        <button
                            onClick={clearFilters}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors shrink-0"
                        >
                            <X className="h-3.5 w-3.5" />
                            Limpiar filtros
                        </button>
                    )}
                </div>
            </div>

            {/* ── Table ── */}
            <div className="rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/50 shadow-sm overflow-hidden">
                {isLoading ? (
                    <div className="p-12 text-center">
                        <Loader2 className="h-6 w-6 animate-spin text-orange-600 mx-auto mb-3" />
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                            Cargando cotizaciones...
                        </p>
                    </div>
                ) : cotizaciones.length === 0 ? (
                    <div className="p-12 text-center">
                        <FileText className="h-12 w-12 text-gray-300 dark:text-gray-700 mx-auto mb-3" />
                        <p className="text-gray-500 dark:text-gray-400 font-medium">
                            {hasActiveFilters
                                ? "No se encontraron cotizaciones con los filtros aplicados"
                                : "No hay cotizaciones aún"}
                        </p>
                        {hasActiveFilters && (
                            <button
                                onClick={clearFilters}
                                className="mt-3 text-sm text-orange-600 hover:text-orange-700 font-medium"
                            >
                                Limpiar filtros
                            </button>
                        )}
                    </div>
                ) : (
                    <>
                        {/* Header row */}
                        <div className="grid grid-cols-18 gap-4 px-4 py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-700">
                            <div className="col-span-3">Cotización</div>
                            <div className="col-span-3">Cliente</div>
                            <div className="col-span-2">Total</div>
                            <div className="col-span-2">
                                Estado
                            </div>
                            <div className="col-span-3">Vendedor</div>
                            <div className="col-span-2">Vigencia</div>
                            <div className="col-span-1"></div>
                        </div>

                        {/* Rows */}
                        {cotizaciones.map((cot) => {
                            const cfg =
                                estadoConfig[cot.estado] ??
                                estadoConfig.borrador;
                            const isExpired =
                                cot.fecha_vencimiento &&
                                new Date(cot.fecha_vencimiento) < new Date();
                            const esBorrador = cot.estado === "borrador";

                            return (
                                <div
                                    key={cot.id}
                                    className="grid grid-cols-18 gap-4 items-center px-4 py-3 border-b border-gray-100 dark:border-gray-800 last:border-0 hover:bg-gray-50/50 dark:hover:bg-gray-800/20 transition-colors"
                                >
                                    {/* Cotización */}
                                    <div className="col-span-3 flex items-center gap-2">
                                        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-orange-50 dark:bg-orange-900/20 shrink-0">
                                            <FileText className="h-4 w-4 text-orange-600 dark:text-orange-400" />
                                        </div>
                                        <div className="min-w-0">
                                            <div className="font-semibold text-gray-900 dark:text-gray-100 text-sm truncate">
                                                {cot.numero_cotizacion}
                                            </div>
                                            <div className="text-xs text-gray-500 dark:text-gray-400">
                                                {formatDate(cot.created_at)}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Cliente */}
                                    <div className="col-span-3 text-sm text-gray-700 dark:text-gray-300 truncate">
                                        {clienteMap.get(cot.cliente_id) ??
                                            `ID: ${cot.cliente_id}`}
                                    </div>

                                    {/* Total */}
                                    <div className="col-span-2">
                                        <div className="font-semibold text-gray-900 dark:text-gray-100 text-sm">
                                            {formatCurrency(
                                                cot.total,
                                                cot.moneda
                                            )}
                                        </div>
                                        <div className="text-xs text-gray-400 dark:text-gray-500">
                                            IGV:{" "}
                                            {formatCurrency(
                                                cot.igv_total,
                                                cot.moneda
                                            )}
                                        </div>
                                    </div>

                                    {/* Estado */}
                                    <div className="col-span-2 flex">
                                        <span
                                            className={clsx(
                                                "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium",
                                                cfg.classes
                                            )}
                                        >
                                            {cfg.label}
                                        </span>
                                    </div>

                                    {/* Vendedor */}
                                    <div className="col-span-3 text-sm text-gray-600 dark:text-gray-400 truncate">
                                        {vendedorMap.get(cot.usuario_id) ??
                                            `ID: ${cot.usuario_id}`}
                                    </div>

                                    {/* Vigencia */}
                                    <div className="col-span-4 flex items-center gap-1 text-sm">
                                        <CalendarDays className="h-3.5 w-3.5 text-gray-400 shrink-0" />
                                        <span
                                            className={clsx(
                                                isExpired
                                                    ? "text-red-600 dark:text-red-400"
                                                    : "text-gray-600 dark:text-gray-400",
                                                "truncate"
                                            )}
                                        >
                                            {formatDate(
                                                cot.fecha_vencimiento
                                            )}
                                        </span>
                                    </div>

                                    {/* Actions */}
                                    <div className="col-span-1 flex items-center justify-end gap-1">
                                        {esBorrador && (
                                            <Link
                                                href={`/dashboard/cotizaciones/${cot.id}/editar`}
                                                onClick={(e) =>
                                                    e.stopPropagation()
                                                }
                                                className="p-1.5 rounded-lg text-gray-500 hover:text-orange-600 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-colors"
                                            >
                                                <Pencil className="h-4 w-4" />
                                            </Link>
                                        )}
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleDescargarPdf(cot.id);
                                            }}
                                            className="p-1.5 rounded-lg text-gray-500 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
                                        >
                                            <FileDown className="h-4 w-4" />
                                        </button>
                                        {esBorrador && (
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    setDeletingCotizacion(cot);
                                                }}
                                                className="p-1.5 rounded-lg text-gray-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </button>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </>
                )}
            </div>

            {/* Delete Confirm */}
            <ConfirmDialog
                open={!!deletingCotizacion}
                onClose={() => setDeletingCotizacion(null)}
                onConfirm={handleEliminar}
                variant="destructive"
                title="Eliminar Cotización"
                description={`¿Estás seguro de que deseas eliminar la cotización "${deletingCotizacion?.numero_cotizacion}"? Esta acción no se puede deshacer.`}
                confirmLabel="Sí, eliminar"
            />
        </div>
    );
}
