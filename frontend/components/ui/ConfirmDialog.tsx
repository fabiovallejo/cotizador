"use client";

import * as React from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { AlertTriangle, X, Loader2 } from "lucide-react";

export interface ConfirmDialogProps {
    open: boolean;
    onClose: () => void;
    onConfirm: () => Promise<void> | void;
    title: string;
    description: string;
    /** Text for the confirm button */
    confirmLabel?: string;
    /** Visual variant — destructive shows red styling */
    variant?: "destructive" | "default";
}

export function ConfirmDialog({
    open,
    onClose,
    onConfirm,
    title,
    description,
    confirmLabel = "Confirmar",
    variant = "default",
}: ConfirmDialogProps) {
    const [isLoading, setIsLoading] = React.useState(false);

    const handleConfirm = async () => {
        setIsLoading(true);
        try {
            await onConfirm();
            onClose();
        } catch (err) {
            console.error("ConfirmDialog error:", err);
        } finally {
            setIsLoading(false);
        }
    };

    const isDestructive = variant === "destructive";

    return (
        <Dialog.Root open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
            <Dialog.Portal>
                <Dialog.Overlay className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />

                <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-2xl shadow-black/10 dark:shadow-black/40 focus:outline-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%]">
                    <div className="p-6">
                        {/* Icon + Close */}
                        <div className="flex items-start justify-between">
                            <div className={`flex items-center justify-center w-12 h-12 rounded-full ${isDestructive
                                ? "bg-red-50 dark:bg-red-900/20"
                                : "bg-orange-50 dark:bg-orange-900/20"
                                }`}>
                                <AlertTriangle className={`h-6 w-6 ${isDestructive
                                    ? "text-red-600 dark:text-red-400"
                                    : "text-orange-600 dark:text-orange-400"
                                    }`} />
                            </div>
                            <Dialog.Close asChild>
                                <button className="rounded-lg p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                                    <X className="h-5 w-5" />
                                </button>
                            </Dialog.Close>
                        </div>

                        {/* Content */}
                        <div className="mt-4">
                            <Dialog.Title className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                                {title}
                            </Dialog.Title>
                            <Dialog.Description className="mt-2 text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                                {description}
                            </Dialog.Description>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center justify-end gap-3 mt-6">
                            <button
                                type="button"
                                onClick={onClose}
                                disabled={isLoading}
                                className="rounded-xl border border-gray-200 dark:border-gray-700 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                            >
                                Cancelar
                            </button>
                            <button
                                type="button"
                                onClick={handleConfirm}
                                disabled={isLoading}
                                className={`inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium text-white shadow-lg transition-all disabled:opacity-60 disabled:cursor-not-allowed ${isDestructive
                                    ? "bg-red-600 shadow-red-500/20 hover:bg-red-700 hover:shadow-red-500/30"
                                    : "bg-orange-600 shadow-orange-500/20 hover:bg-orange-700 hover:shadow-orange-500/30"
                                    }`}
                            >
                                {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
                                {isLoading ? "Procesando..." : confirmLabel}
                            </button>
                        </div>
                    </div>
                </Dialog.Content>
            </Dialog.Portal>
        </Dialog.Root>
    );
}
