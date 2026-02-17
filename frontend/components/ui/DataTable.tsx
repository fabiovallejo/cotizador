"use client";

import * as React from "react";
import { ChevronDown, ChevronUp, ChevronsUpDown, Search, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

export interface Column<T> {
    header: string;
    accessor: keyof T | ((item: T) => React.ReactNode);
    className?: string;
    sortable?: boolean;
}

interface DataTableProps<T> {
    columns: Column<T>[];
    data: T[];
    onRowClick?: (item: T) => void;
    isLoading?: boolean;
    searchable?: boolean;
    searchKeys?: (keyof T)[];
    pageSize?: number;
}

const PAGE_SIZE_OPTIONS = [25, 50, 100];

export function DataTable<T extends { id?: string | number }>({
    columns,
    data,
    onRowClick,
    isLoading,
    searchable = false,
    searchKeys = [],
    pageSize: initialPageSize = 25,
}: DataTableProps<T>) {
    const [sortConfig, setSortConfig] = React.useState<{
        key: keyof T | null;
        direction: "asc" | "desc" | null;
    }>({ key: null, direction: null });
    const [searchTerm, setSearchTerm] = React.useState("");
    const [currentPage, setCurrentPage] = React.useState(1);
    const [pageSize, setPageSize] = React.useState(initialPageSize);

    const handleSort = (key: keyof T) => {
        let direction: "asc" | "desc" = "asc";
        if (sortConfig.key === key && sortConfig.direction === "asc") {
            direction = "desc";
        }
        setSortConfig({ key, direction });
    };

    const filteredData = React.useMemo(() => {
        if (!searchTerm || searchKeys.length === 0) return data;
        return data.filter((item) =>
            searchKeys.some((key) => {
                const val = item[key];
                return String(val).toLowerCase().includes(searchTerm.toLowerCase());
            })
        );
    }, [data, searchTerm, searchKeys]);

    const sortedData = React.useMemo(() => {
        if (!sortConfig.key || !sortConfig.direction) return filteredData;

        return [...filteredData].sort((a, b) => {
            const aVal = a[sortConfig.key as keyof T];
            const bVal = b[sortConfig.key as keyof T];

            if (aVal === bVal) return 0;
            if (aVal === null || aVal === undefined) return 1;
            if (bVal === null || bVal === undefined) return -1;

            const compare = aVal < bVal ? -1 : 1;
            return sortConfig.direction === "asc" ? compare : -compare;
        });
    }, [filteredData, sortConfig]);

    // Pagination
    const totalItems = sortedData.length;
    const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));

    // Reset to page 1 when data, search, or page size changes
    React.useEffect(() => {
        setCurrentPage(1);
    }, [data, searchTerm, pageSize]);

    const paginatedData = React.useMemo(() => {
        const start = (currentPage - 1) * pageSize;
        return sortedData.slice(start, start + pageSize);
    }, [sortedData, currentPage, pageSize]);

    const startItem = totalItems > 0 ? (currentPage - 1) * pageSize + 1 : 0;
    const endItem = Math.min(currentPage * pageSize, totalItems);

    if (isLoading) {
        return (
            <div className="w-full space-y-4 animate-pulse">
                <div className="h-10 w-1/4 bg-gray-200 dark:bg-gray-800 rounded-lg"></div>
                <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/50 overflow-hidden">
                    <div className="h-12 bg-gray-100 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-800"></div>
                    {[...Array(5)].map((_, i) => (
                        <div key={i} className="h-16 border-b border-gray-200 dark:border-gray-800/50"></div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="w-full space-y-4">
            {searchable && (
                <div className="relative w-full max-w-sm">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500 dark:text-gray-400" />
                    <input
                        type="text"
                        placeholder="Buscar..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full rounded-xl border border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-gray-900/50 pl-10 pr-4 py-2 text-sm outline-none ring-offset-white dark:ring-offset-gray-950 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all backdrop-blur-xl"
                    />
                </div>
            )}

            <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/50 shadow-sm overflow-hidden backdrop-blur-xl transition-all hover:shadow-md hover:border-orange-500/20">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500 dark:text-gray-400 font-medium border-b border-gray-200 dark:border-gray-800">
                            <tr>
                                {columns.map((col, idx) => (
                                    <th
                                        key={idx}
                                        className={cn(
                                            "px-6 py-4 whitespace-nowrap transition-colors",
                                            col.sortable && "cursor-pointer hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100/50 dark:hover:bg-gray-800",
                                            col.className
                                        )}
                                        onClick={() =>
                                            col.sortable && typeof col.accessor !== "function"
                                                ? handleSort(col.accessor as keyof T)
                                                : undefined
                                        }
                                    >
                                        <div className="flex items-center gap-2">
                                            {col.header}
                                            {col.sortable && typeof col.accessor !== "function" && (
                                                <span className="text-xs">
                                                    {sortConfig.key === col.accessor ? (
                                                        sortConfig.direction === "asc" ? (
                                                            <ChevronUp className="h-3 w-3" />
                                                        ) : (
                                                            <ChevronDown className="h-3 w-3" />
                                                        )
                                                    ) : (
                                                        <ChevronsUpDown className="h-3 w-3 opacity-50" />
                                                    )}
                                                </span>
                                            )}
                                        </div>
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
                            {paginatedData.length > 0 ? (
                                paginatedData.map((item, rowIdx) => (
                                    <tr
                                        key={item.id || rowIdx}
                                        onClick={() => onRowClick && onRowClick(item)}
                                        className={cn(
                                            "group transition-colors hover:bg-orange-50/50 dark:hover:bg-orange-950/10",
                                            onRowClick && "cursor-pointer"
                                        )}
                                    >
                                        {columns.map((col, colIdx) => (
                                            <td key={colIdx} className={cn("px-6 py-4", col.className)}>
                                                {typeof col.accessor === "function"
                                                    ? col.accessor(item)
                                                    : (item[col.accessor] as React.ReactNode)}
                                            </td>
                                        ))}
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={columns.length} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                                        <div className="flex flex-col items-center gap-2">
                                            <p className="text-lg font-medium">No se encontraron datos</p>
                                            <p className="text-sm">Intenta ajustar tu búsqueda o filtros.</p>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Pagination controls */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 px-1 text-sm text-gray-500 dark:text-gray-400">
                {/* Left: item count + page size selector */}
                <div className="flex items-center gap-3">
                    <p>
                        Mostrando <span className="font-medium text-gray-700 dark:text-gray-300">{startItem}</span>–<span className="font-medium text-gray-700 dark:text-gray-300">{endItem}</span> de <span className="font-medium text-gray-700 dark:text-gray-300">{totalItems}</span>
                    </p>
                    <div className="flex items-center gap-1.5">
                        <span className="text-xs">Filas:</span>
                        <select
                            value={pageSize}
                            onChange={(e) => setPageSize(Number(e.target.value))}
                            className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-2 py-1 text-xs outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500/20 cursor-pointer"
                        >
                            {PAGE_SIZE_OPTIONS.map((size) => (
                                <option key={size} value={size}>{size}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Right: page navigation */}
                {totalPages > 1 && (
                    <div className="flex items-center gap-1">
                        <button
                            onClick={() => setCurrentPage(1)}
                            disabled={currentPage === 1}
                            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            title="Primera página"
                        >
                            <ChevronsLeft className="h-4 w-4" />
                        </button>
                        <button
                            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            title="Anterior"
                        >
                            <ChevronLeft className="h-4 w-4" />
                        </button>

                        {/* Page numbers */}
                        {(() => {
                            const pages: number[] = [];
                            let start = Math.max(1, currentPage - 2);
                            let end = Math.min(totalPages, currentPage + 2);

                            // Adjust window
                            if (end - start < 4) {
                                if (start === 1) end = Math.min(totalPages, start + 4);
                                else start = Math.max(1, end - 4);
                            }

                            for (let i = start; i <= end; i++) pages.push(i);

                            return pages.map((page) => (
                                <button
                                    key={page}
                                    onClick={() => setCurrentPage(page)}
                                    className={cn(
                                        "min-w-[2rem] h-8 rounded-lg text-xs font-medium transition-colors",
                                        page === currentPage
                                            ? "bg-orange-600 text-white shadow-sm"
                                            : "hover:bg-gray-100 dark:hover:bg-gray-800"
                                    )}
                                >
                                    {page}
                                </button>
                            ));
                        })()}

                        <button
                            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                            disabled={currentPage === totalPages}
                            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            title="Siguiente"
                        >
                            <ChevronRight className="h-4 w-4" />
                        </button>
                        <button
                            onClick={() => setCurrentPage(totalPages)}
                            disabled={currentPage === totalPages}
                            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            title="Última página"
                        >
                            <ChevronsRight className="h-4 w-4" />
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
