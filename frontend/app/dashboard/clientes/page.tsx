"use client";

import { useState, useEffect } from "react";
import { DataTable, type Column } from "@/components/ui/DataTable";
import { EditModal, type FieldConfig } from "@/components/ui/EditModal";
import { listarClientes, actualizarCliente, crearCliente } from "@/services/clientes.service";
import type { Cliente } from "@/types/clientes";
import { Plus, Pencil, Trash2, Mail, Phone } from "lucide-react";
import { toast } from "sonner";
import { clsx } from "clsx";

/* ── Field configuration for the edit modal ── */
const clienteFields: FieldConfig<Cliente>[] = [
    {
        key: "tipo_documento", label: "Tipo Documento", type: "select", required: true, options: [
            { value: "DNI", label: "DNI" },
            { value: "RUC", label: "RUC" },
            { value: "CE", label: "Carné de Extranjería" },
            { value: "PASAPORTE", label: "Pasaporte" },
        ]
    },
    { key: "numero_documento", label: "Nro. Documento", type: "text", required: true, readOnly: true },
    { key: "razon_social", label: "Razón Social", type: "text", required: true, fullWidth: true },
    { key: "nombre_comercial", label: "Nombre Comercial", type: "text", fullWidth: true },
    { key: "email", label: "Email", type: "email", placeholder: "correo@ejemplo.com" },
    { key: "telefono", label: "Teléfono", type: "tel", placeholder: "+51 999 999 999" },
    { key: "direccion_completa", label: "Dirección", type: "textarea", fullWidth: true, placeholder: "Av. Principal 123, Lima" },
    { key: "ubigeo", label: "Ubigeo", type: "text", placeholder: "150101" },
    { key: "es_cliente_frecuente", label: "Cliente Frecuente", type: "checkbox", placeholder: "Marcar como cliente frecuente" },
    {
        key: "estado", label: "Estado", type: "select", required: true, options: [
            { value: "activo", label: "Activo" },
            { value: "inactivo", label: "Inactivo" },
        ]
    },
];

export default function ClientesPage() {
    const [clientes, setClientes] = useState<Cliente[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [editingCliente, setEditingCliente] = useState<Cliente | null>(null);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

    useEffect(() => {
        const fetchClientes = async () => {
            try {
                const data = await listarClientes();
                setClientes(data);
            } catch (error) {
                console.error("Error fetching clientes:", error);
                toast.error("Error al cargar los clientes");
            } finally {
                setIsLoading(false);
            }
        };

        fetchClientes();
    }, []);

    const handleEditarCliente = (cliente: Cliente) => {
        setEditingCliente(cliente);
        setIsEditModalOpen(true);
    };

    const handleGuardarCliente = async (updated: Cliente) => {
        try {
            const saved = await actualizarCliente(updated);
            setClientes((prev) =>
                prev.map((c) => (c.id === saved.id ? saved : c))
            );
            toast.success("Cliente actualizado exitosamente");
        } catch (error) {
            console.error("Error updating cliente:", error);
            toast.error("Error al actualizar el cliente");
            throw error;
        }
    };

    const handleCrearNuevoCliente = async (data: Cliente) => {
        try {
            const nuevo = await crearCliente(data);
            setClientes((prev) => [...prev, nuevo]);
            toast.success("Cliente creado exitosamente");
        } catch (error) {
            console.error("Error creating cliente:", error);
            toast.error("Error al crear el cliente");
            throw error;
        }
    };

    const columns: Column<Cliente>[] = [
        {
            header: "Cliente",
            accessor: (cliente) => (
                <div className="flex flex-col">
                    <span className="font-medium text-gray-900 dark:text-gray-100">{cliente.razon_social}</span>
                    {cliente.nombre_comercial && (
                        <span className="text-xs text-gray-500 dark:text-gray-400">{cliente.nombre_comercial}</span>
                    )}
                </div>
            ),
            sortable: true,
        },
        {
            header: "Documento",
            accessor: (cliente) => (
                <div className="flex flex-col">
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                        {cliente.tipo_documento}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">
                        {cliente.numero_documento}
                    </span>
                </div>
            ),
            sortable: true,
        },
        {
            header: "Contacto",
            accessor: (cliente) => (
                <div className="flex flex-col gap-1">
                    {cliente.email && (
                        <div className="flex items-center gap-1.5 text-xs text-gray-600 dark:text-gray-400">
                            <Mail className="h-3 w-3" />
                            <span className="truncate max-w-[200px]">{cliente.email}</span>
                        </div>
                    )}
                    {cliente.telefono && (
                        <div className="flex items-center gap-1.5 text-xs text-gray-600 dark:text-gray-400">
                            <Phone className="h-3 w-3" />
                            <span>{cliente.telefono}</span>
                        </div>
                    )}
                </div>
            )
        },
        {
            header: "Estado",
            accessor: (cliente) => (
                <span
                    className={clsx(
                        "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium",
                        cliente.estado === "activo"
                            ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                            : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                    )}
                >
                    {cliente.estado}
                </span>
            ),
            sortable: true,
        },
        {
            header: "",
            accessor: (cliente) => (
                <div className="flex items-center justify-end gap-2">
                    <button
                        onClick={(e) => { e.stopPropagation(); handleEditarCliente(cliente); }}
                        className="p-1.5 rounded-lg text-gray-500 hover:text-orange-600 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-colors"
                    >
                        <Pencil className="h-4 w-4" />
                    </button>
                    <button className="p-1.5 rounded-lg text-gray-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors">
                        <Trash2 className="h-4 w-4" />
                    </button>
                </div>
            ),
            className: "w-[100px]",
        },
    ];

    return (
        <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
                        Clientes <span className="text-s text-gray-500 dark:text-gray-400">({clientes.length})</span>
                    </h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-1">
                        Gestiona tu cartera de clientes y sus datos.
                    </p>
                </div>
                <button
                    onClick={() => setIsCreateModalOpen(true)}
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-orange-600 px-4 py-2 text-sm font-medium text-white shadow-lg shadow-orange-500/20 hover:bg-orange-700 hover:shadow-orange-500/30 transition-all focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 cursor-pointer"
                >
                    <Plus className="h-4 w-4" />
                    Nuevo Cliente
                </button>
            </div>

            {/* Table Section */}
            <div className="space-y-4">
                <DataTable
                    columns={columns}
                    data={clientes}
                    isLoading={isLoading}
                    searchable={true}
                    searchKeys={["razon_social", "numero_documento", "email", "nombre_comercial"]}
                />
            </div>

            {/* Edit Modal */}
            <EditModal<Cliente>
                open={isEditModalOpen}
                onClose={() => { setIsEditModalOpen(false); setEditingCliente(null); }}
                title="Editar Cliente"
                description="Modifica los datos del cliente seleccionado."
                item={editingCliente}
                fields={clienteFields}
                onSave={handleGuardarCliente}
            />

            {/* Create Modal */}
            <EditModal<Cliente>
                open={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                mode="create"
                title="Nuevo Cliente"
                description="Registra un nuevo cliente en el sistema."
                fields={clienteFields.map((f) =>
                    f.key === "numero_documento" ? { ...f, readOnly: false } : f
                )}
                defaultValues={{ tipo_documento: "RUC", estado: "activo", es_cliente_frecuente: false } as Partial<Cliente>}
                onSave={handleCrearNuevoCliente}
                submitLabel="Registrar Cliente"
            />
        </div>
    );
}
