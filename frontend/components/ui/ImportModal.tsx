"use client";

import { useState, useRef, useCallback } from "react";
import { Upload, Download, FileSpreadsheet, X, CheckCircle2, AlertTriangle, Loader2 } from "lucide-react";

interface ImportResult {
    creados: number;
    errores: { fila: number | string; error: string }[];
}

interface ImportModalProps {
    open: boolean;
    onClose: () => void;
    title: string;
    entityName: string; // "clientes" or "productos"
    onDownloadTemplate: () => Promise<Blob>;
    onImport: (file: File) => Promise<ImportResult>;
    onSuccess?: () => void;
    templateFilename: string;
}

export function ImportModal({
    open,
    onClose,
    title,
    entityName,
    onDownloadTemplate,
    onImport,
    onSuccess,
    templateFilename,
}: ImportModalProps) {
    const [step, setStep] = useState<"upload" | "loading" | "result">("upload");
    const [file, setFile] = useState<File | null>(null);
    const [result, setResult] = useState<ImportResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [downloading, setDownloading] = useState(false);
    const [dragOver, setDragOver] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    const reset = useCallback(() => {
        setStep("upload");
        setFile(null);
        setResult(null);
        setError(null);
    }, []);

    const handleClose = () => {
        reset();
        onClose();
    };

    const handleDownloadTemplate = async () => {
        setDownloading(true);
        try {
            const blob = await onDownloadTemplate();
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = templateFilename;
            a.click();
            URL.revokeObjectURL(url);
        } catch {
            setError("Error al descargar la plantilla");
        } finally {
            setDownloading(false);
        }
    };

    const handleFileSelect = (f: File) => {
        if (!f.name.endsWith(".xlsx")) {
            setError("Solo se aceptan archivos .xlsx");
            return;
        }
        if (f.size > 5 * 1024 * 1024) {
            setError("El archivo excede los 5MB");
            return;
        }
        setError(null);
        setFile(f);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setDragOver(false);
        const f = e.dataTransfer.files[0];
        if (f) handleFileSelect(f);
    };

    const handleImport = async () => {
        if (!file) return;
        setStep("loading");
        setError(null);
        try {
            const res = await onImport(file);
            setResult(res);
            setStep("result");
            if (res.creados > 0 && onSuccess) onSuccess();
        } catch (e: any) {
            setError(e.message || "Error al importar");
            setStep("upload");
        }
    };

    if (!open) return null;

    return (
        <>
            {/* Backdrop */}
            <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm" onClick={handleClose} />

            {/* Modal */}
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <div
                    className="w-full max-w-lg bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden"
                    onClick={(e) => e.stopPropagation()}
                >
                    {/* Header */}
                    <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-800">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-900/20">
                                <FileSpreadsheet className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                            </div>
                            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{title}</h2>
                        </div>
                        <button onClick={handleClose} className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                            <X className="h-5 w-5" />
                        </button>
                    </div>

                    {/* Body */}
                    <div className="px-6 py-5 space-y-5">

                        {/* Step 1: Download template */}
                        <div className="flex items-start gap-4 p-4 rounded-xl bg-blue-50/50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-900/30">
                            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-bold text-sm shrink-0">
                                1
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">Descargar plantilla</p>
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                                    Los campos en <span className="text-orange-600 font-semibold">naranja</span> son obligatorios, los <span className="text-gray-500 font-semibold">grises</span> son opcionales.
                                </p>
                                <button
                                    onClick={handleDownloadTemplate}
                                    disabled={downloading}
                                    className="mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-blue-700 bg-blue-100 hover:bg-blue-200 dark:text-blue-300 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 transition-colors disabled:opacity-50"
                                >
                                    {downloading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Download className="h-3.5 w-3.5" />}
                                    {templateFilename}
                                </button>
                            </div>
                        </div>

                        {/* Step 2: Upload file */}
                        {step === "upload" && (
                            <div className="space-y-3">
                                <div className="flex items-start gap-4">
                                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 font-bold text-sm shrink-0">
                                        2
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">Subir archivo lleno</p>
                                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                                            Máximo 5MB, formato .xlsx
                                        </p>
                                    </div>
                                </div>

                                {/* Drop zone */}
                                <div
                                    onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                                    onDragLeave={() => setDragOver(false)}
                                    onDrop={handleDrop}
                                    onClick={() => inputRef.current?.click()}
                                    className={`
                                        ml-12 p-6 rounded-xl border-2 border-dashed cursor-pointer transition-all
                                        ${dragOver
                                            ? "border-emerald-400 bg-emerald-50/50 dark:bg-emerald-900/10"
                                            : file
                                                ? "border-emerald-300 bg-emerald-50/30 dark:bg-emerald-900/10"
                                                : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800/50"
                                        }
                                    `}
                                >
                                    <input
                                        ref={inputRef}
                                        type="file"
                                        accept=".xlsx"
                                        className="hidden"
                                        onChange={(e) => {
                                            const f = e.target.files?.[0];
                                            if (f) handleFileSelect(f);
                                        }}
                                    />
                                    <div className="text-center">
                                        {file ? (
                                            <div className="flex items-center justify-center gap-2">
                                                <FileSpreadsheet className="h-5 w-5 text-emerald-600" />
                                                <span className="text-sm font-medium text-emerald-700 dark:text-emerald-400">{file.name}</span>
                                                <span className="text-xs text-gray-400">({(file.size / 1024).toFixed(0)} KB)</span>
                                            </div>
                                        ) : (
                                            <>
                                                <Upload className="h-8 w-8 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
                                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                                    Arrastra tu archivo aquí o <span className="text-blue-600 dark:text-blue-400 font-medium">haz click para seleccionar</span>
                                                </p>
                                            </>
                                        )}
                                    </div>
                                </div>

                                {/* Error */}
                                {error && (
                                    <div className="ml-12 flex items-center gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/30">
                                        <AlertTriangle className="h-4 w-4 text-red-500 shrink-0" />
                                        <p className="text-xs text-red-600 dark:text-red-400">{error}</p>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Loading */}
                        {step === "loading" && (
                            <div className="flex flex-col items-center py-8 space-y-3">
                                <Loader2 className="h-8 w-8 animate-spin text-emerald-500" />
                                <p className="text-sm text-gray-500 dark:text-gray-400">Importando {entityName}...</p>
                                <p className="text-xs text-gray-400">Procesando por lotes para evitar timeouts</p>
                            </div>
                        )}

                        {/* Result */}
                        {step === "result" && result && (
                            <div className="space-y-4">
                                {/* Success summary */}
                                <div className="flex items-center gap-3 p-4 rounded-xl bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-100 dark:border-emerald-900/30">
                                    <CheckCircle2 className="h-6 w-6 text-emerald-500 shrink-0" />
                                    <div>
                                        <p className="text-sm font-semibold text-emerald-700 dark:text-emerald-400">
                                            {result.creados} {entityName} importado(s) correctamente
                                        </p>
                                        {result.errores.length > 0 && (
                                            <p className="text-xs text-amber-600 dark:text-amber-400 mt-0.5">
                                                {result.errores.length} fila(s) con errores
                                            </p>
                                        )}
                                    </div>
                                </div>

                                {/* Errors list */}
                                {result.errores.length > 0 && (
                                    <div className="max-h-48 overflow-y-auto rounded-xl border border-red-100 dark:border-red-900/30">
                                        <table className="w-full text-xs">
                                            <thead>
                                                <tr className="bg-red-50 dark:bg-red-900/10">
                                                    <th className="text-left px-3 py-2 text-red-500 font-medium w-16">Fila</th>
                                                    <th className="text-left px-3 py-2 text-red-500 font-medium">Error</th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-red-50 dark:divide-red-900/10">
                                                {result.errores.map((err, idx) => (
                                                    <tr key={idx} className="hover:bg-red-50/50 dark:hover:bg-red-900/5">
                                                        <td className="px-3 py-1.5 text-gray-600 dark:text-gray-400 font-mono">{err.fila}</td>
                                                        <td className="px-3 py-1.5 text-red-600 dark:text-red-400">{err.error}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Footer */}
                    <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/30">
                        {step === "result" ? (
                            <button
                                onClick={handleClose}
                                className="px-4 py-2 rounded-xl text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 transition-colors"
                            >
                                Cerrar
                            </button>
                        ) : step === "upload" ? (
                            <>
                                <button
                                    onClick={handleClose}
                                    className="px-4 py-2 rounded-xl text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                                >
                                    Cancelar
                                </button>
                                <button
                                    onClick={handleImport}
                                    disabled={!file}
                                    className="px-4 py-2 rounded-xl text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-lg shadow-emerald-500/20"
                                >
                                    <span className="flex items-center gap-1.5">
                                        <Upload className="h-4 w-4" />
                                        Importar
                                    </span>
                                </button>
                            </>
                        ) : null}
                    </div>
                </div>
            </div>
        </>
    );
}
