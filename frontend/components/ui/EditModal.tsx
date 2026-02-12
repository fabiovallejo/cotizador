"use client";

import * as React from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { X, Loader2 } from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

/* ───────────────────────────── Types ───────────────────────────── */

export type FieldType = "text" | "email" | "tel" | "number" | "select" | "checkbox" | "textarea";

export interface FieldConfig<T> {
    /** Key of the object being edited */
    key: keyof T;
    /** Label shown above the input */
    label: string;
    /** Input type */
    type: FieldType;
    /** Placeholder text */
    placeholder?: string;
    /** Whether the field is required */
    required?: boolean;
    /** Whether this field is read-only (displayed but not editable) */
    readOnly?: boolean;
    /** Options for select fields */
    options?: { value: string; label: string }[];
    /** Extra CSS class for the field wrapper */
    className?: string;
    /** Span full width (col-span-2) */
    fullWidth?: boolean;
}

export interface EditModalProps<T extends object> {
    /** Whether the modal is open */
    open: boolean;
    /** Callback when the modal should close */
    onClose: () => void;
    /** Title displayed at the top of the modal */
    title: string;
    /** Optional subtitle / description */
    description?: string;
    /** The item being edited — used to populate the form (ignored in create mode) */
    item?: T | null;
    /** Default values for a new item (used in create mode) */
    defaultValues?: Partial<T>;
    /** Field configuration array — drives the form layout */
    fields: FieldConfig<T>[];
    /** Callback when the user submits the form. Receives the updated object. */
    onSave: (updated: T) => Promise<void> | void;
    /** Modal mode: 'edit' populates from item, 'create' starts empty/defaults */
    mode?: "edit" | "create";
    /** Custom submit button label */
    submitLabel?: string;
}

/* ───────────────────────────── Component ───────────────────────────── */

export function EditModal<T extends object>({
    open,
    onClose,
    title,
    description,
    item,
    defaultValues,
    fields,
    onSave,
    mode = "edit",
    submitLabel,
}: EditModalProps<T>) {
    const [formData, setFormData] = React.useState<Partial<T>>({});
    const [isSaving, setIsSaving] = React.useState(false);

    const isCreateMode = mode === "create";

    // Sync form data when the item or mode changes
    React.useEffect(() => {
        if (open) {
            if (isCreateMode) {
                setFormData(defaultValues ? { ...defaultValues } : {});
            } else if (item) {
                setFormData({ ...item });
            }
        }
    }, [item, open, isCreateMode, defaultValues]);

    const handleChange = (key: keyof T, value: unknown) => {
        setFormData((prev) => ({ ...prev, [key]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        try {
            await onSave(formData as T);
            onClose();
        } catch (err) {
            console.error("Error saving:", err);
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <Dialog.Root open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
            <Dialog.Portal>
                {/* Overlay */}
                <Dialog.Overlay className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />

                {/* Content */}
                <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-full max-w-lg -translate-x-1/2 -translate-y-1/2 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-2xl shadow-black/10 dark:shadow-black/40 focus:outline-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%]">
                    {/* Header */}
                    <div className="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 px-6 py-4">
                        <div>
                            <Dialog.Title className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                                {title}
                            </Dialog.Title>
                            {description && (
                                <Dialog.Description className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                                    {description}
                                </Dialog.Description>
                            )}
                        </div>
                        <Dialog.Close asChild>
                            <button className="rounded-lg p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                                <X className="h-5 w-5" />
                            </button>
                        </Dialog.Close>
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSubmit}>
                        <div className="px-6 py-5 max-h-[60vh] overflow-y-auto">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {fields.map((field) => {
                                    const value = formData[field.key];
                                    return (
                                        <div
                                            key={String(field.key)}
                                            className={cn(
                                                "flex flex-col gap-1.5",
                                                field.fullWidth && "md:col-span-2",
                                                field.className
                                            )}
                                        >
                                            <label
                                                htmlFor={String(field.key)}
                                                className="text-sm font-medium text-gray-700 dark:text-gray-300"
                                            >
                                                {field.label}
                                                {field.required && <span className="text-orange-500 ml-0.5">*</span>}
                                            </label>

                                            {/* ─── Select ─── */}
                                            {field.type === "select" ? (
                                                <select
                                                    id={String(field.key)}
                                                    value={String(value ?? "")}
                                                    onChange={(e) => handleChange(field.key, e.target.value)}
                                                    disabled={field.readOnly}
                                                    className={cn(
                                                        "w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50 px-3 py-2 text-sm outline-none transition-all",
                                                        "focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20",
                                                        field.readOnly && "opacity-60 cursor-not-allowed"
                                                    )}
                                                >
                                                    {field.options?.map((opt) => (
                                                        <option key={opt.value} value={opt.value}>
                                                            {opt.label}
                                                        </option>
                                                    ))}
                                                </select>

                                            ) : field.type === "checkbox" ? (
                                                /* ─── Checkbox ─── */
                                                <label className="inline-flex items-center gap-2 cursor-pointer">
                                                    <input
                                                        id={String(field.key)}
                                                        type="checkbox"
                                                        checked={Boolean(value)}
                                                        onChange={(e) => handleChange(field.key, e.target.checked)}
                                                        disabled={field.readOnly}
                                                        className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-orange-600 focus:ring-orange-500"
                                                    />
                                                    <span className="text-sm text-gray-600 dark:text-gray-400">
                                                        {field.placeholder ?? "Sí"}
                                                    </span>
                                                </label>

                                            ) : field.type === "textarea" ? (
                                                /* ─── Textarea ─── */
                                                <textarea
                                                    id={String(field.key)}
                                                    value={String(value ?? "")}
                                                    onChange={(e) => handleChange(field.key, e.target.value)}
                                                    placeholder={field.placeholder}
                                                    required={field.required}
                                                    readOnly={field.readOnly}
                                                    rows={3}
                                                    className={cn(
                                                        "w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50 px-3 py-2 text-sm outline-none transition-all resize-none",
                                                        "focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20",
                                                        field.readOnly && "opacity-60 cursor-not-allowed"
                                                    )}
                                                />
                                            ) : (
                                                /* ─── Default text/email/tel/number ─── */
                                                <input
                                                    id={String(field.key)}
                                                    type={field.type}
                                                    value={String(value ?? "")}
                                                    onChange={(e) =>
                                                        handleChange(
                                                            field.key,
                                                            field.type === "number" ? Number(e.target.value) : e.target.value
                                                        )
                                                    }
                                                    placeholder={field.placeholder}
                                                    required={field.required}
                                                    readOnly={field.readOnly}
                                                    className={cn(
                                                        "w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50 px-3 py-2 text-sm outline-none transition-all",
                                                        "focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20",
                                                        field.readOnly && "opacity-60 cursor-not-allowed"
                                                    )}
                                                />
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="flex items-center justify-end gap-3 border-t border-gray-100 dark:border-gray-800 px-6 py-4">
                            <button
                                type="button"
                                onClick={onClose}
                                disabled={isSaving}
                                className="rounded-xl border border-gray-200 dark:border-gray-700 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                            >
                                Cancelar
                            </button>
                            <button
                                type="submit"
                                disabled={isSaving}
                                className="inline-flex items-center gap-2 rounded-xl bg-orange-600 px-4 py-2 text-sm font-medium text-white shadow-lg shadow-orange-500/20 hover:bg-orange-700 hover:shadow-orange-500/30 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
                            >
                                {isSaving && <Loader2 className="h-4 w-4 animate-spin" />}
                                {isSaving
                                    ? (isCreateMode ? "Creando..." : "Guardando...")
                                    : (submitLabel ?? (isCreateMode ? "Crear" : "Guardar Cambios"))
                                }
                            </button>
                        </div>
                    </form>
                </Dialog.Content>
            </Dialog.Portal>
        </Dialog.Root>
    );
}
