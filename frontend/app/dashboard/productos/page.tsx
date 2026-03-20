"use client";

import { useState, useEffect } from "react";
import { DataTable, type Column } from "@/components/ui/DataTable";
import { EditModal, type FieldConfig } from "@/components/ui/EditModal";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { ImportModal } from "@/components/ui/ImportModal";
import { listarProductos, actualizarProducto, crearProducto, eliminarProducto, descargarPlantillaProductos, importarProductos } from "@/services/productos.service";
import type { Producto } from "@/types/productos";
import { Plus, Pencil, Trash2, Package, Tag, Wrench, Layers, Upload } from "lucide-react";
import { toast } from "sonner";
import { clsx } from "clsx";
import { useAuth } from "@/hooks/useAuth";

/* ── Field configuration for the modals ── */
const productoFields: FieldConfig<Producto>[] = [
    { key: "codigo", label: "Código / SKU", type: "text", required: true, readOnly: true },
    { key: "nombre", label: "Nombre", type: "text", required: true },
    {
        key: "tipo", label: "Tipo", type: "select", required: true, options: [
            { value: "producto", label: "Producto" },
            { value: "servicio", label: "Servicio" },
            { value: "combo", label: "Combo" },
        ]
    },
    { key: "categoria", label: "Categoría", type: "text", placeholder: "Ej: Tecnología, Alimentos" },
    { key: "marca", label: "Marca", type: "text", placeholder: "Ej: Dell, HP" },
    { key: "descripcion", label: "Descripción", type: "textarea", fullWidth: true, placeholder: "Descripción del producto o servicio" },
    { key: "precio_unitario", label: "Precio Unitario", type: "number", required: true, placeholder: "0.00" },
    { key: "costo_unitario", label: "Costo Unitario", type: "number", placeholder: "0.00" },
    {
        key: "moneda", label: "Moneda", type: "select", required: true, options: [
            { value: "PEN", label: "PEN - Soles" },
            { value: "USD", label: "USD - Dólares" }
        ]
    },
    {
        key: "unidad_medida", label: "Unidad de Medida", type: "select", required: true, options: [
            { value: "UND", label: "Unidad" },
            { value: "KG", label: "Kilogramo" },
            { value: "LTR", label: "Litro" },
            { value: "MT", label: "Metro" },
            { value: "HRA", label: "Hora" },
            { value: "DIA", label: "Día" },
            { value: "SER", label: "Servicio" },
        ]
    },
    { key: "aplica_igv", label: "¿Aplica IGV?", type: "checkbox", placeholder: "Este producto aplica IGV" },
    { key: "igv_porcentaje", label: "% IGV", type: "number", placeholder: "18" },
    {
        key: "tipo_afectacion_igv", label: "Tipo Afectación IGV", type: "select", options: [
            { value: "10", label: "10 - Gravado" },
            { value: "20", label: "20 - Exonerado" },
            { value: "30", label: "30 - Inafecto" },
        ]
    },
    { key: "tiene_stock", label: "¿Controla Stock?", type: "checkbox", placeholder: "Activar control de inventario" },
    { key: "cantidad_stock", label: "Stock Actual", type: "number", placeholder: "0" },
    {
        key: "estado", label: "Estado", type: "select", required: true, options: [
            { value: "activo", label: "Activo" },
            { value: "inactivo", label: "Inactivo" },
        ]
    },
];

/* ── Helpers ── */
const formatCurrency = (value: number, moneda: string) => {
    const symbol = moneda === "USD" ? "$" : moneda === "EUR" ? "€" : "S/";
    return `${symbol} ${Number(value).toFixed(2)}`;
};

const tipoConfig = (tipo: string) => {
    const map: Record<string, { badge: string; iconBg: string; iconColor: string; Icon: typeof Package }> = {
        producto: {
            badge: "bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
            iconBg: "bg-blue-50 dark:bg-blue-900/20",
            iconColor: "text-blue-600 dark:text-blue-400",
            Icon: Package,
        },
        servicio: {
            badge: "bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
            iconBg: "bg-purple-50 dark:bg-purple-900/20",
            iconColor: "text-purple-600 dark:text-purple-400",
            Icon: Wrench,
        },
        combo: {
            badge: "bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
            iconBg: "bg-amber-50 dark:bg-amber-900/20",
            iconColor: "text-amber-600 dark:text-amber-400",
            Icon: Layers,
        },
    };
    return map[tipo] ?? {
        badge: "bg-gray-50 text-gray-700 dark:bg-gray-800 dark:text-gray-400",
        iconBg: "bg-gray-50 dark:bg-gray-800",
        iconColor: "text-gray-600 dark:text-gray-400",
        Icon: Package,
    };
};

export default function ProductosPage() {
    const { user } = useAuth();
    const isAdmin = user?.rol === "administrador" || user?.rol === "admin";
    const [productos, setProductos] = useState<Producto[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [editingProducto, setEditingProducto] = useState<Producto | null>(null);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [deletingProducto, setDeletingProducto] = useState<Producto | null>(null);
    const [isImportModalOpen, setIsImportModalOpen] = useState(false);

    const fetchProductos = async () => {
        setIsLoading(true);
        try {
            const data = await listarProductos();
            setProductos(data);
        } catch (error) {
            console.error("Error fetching productos:", error);
            toast.error("Error al cargar los productos");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchProductos();
    }, []);

    const handleEditarProducto = (producto: Producto) => {
        setEditingProducto(producto);
        setIsEditModalOpen(true);
    };

    const handleGuardarProducto = async (updated: Producto) => {
        try {
            const saved = await actualizarProducto(updated);
            setProductos((prev) =>
                prev.map((p) => (p.id === saved.id ? saved : p))
            );
            toast.success("Producto actualizado exitosamente");
        } catch (error) {
            console.error("Error updating producto:", error);
            toast.error("Error al actualizar el producto");
            throw error;
        }
    };

    const handleCrearNuevoProducto = async (data: Producto) => {
        try {
            const nuevo = await crearProducto(data);
            setProductos((prev) => [...prev, nuevo]);
            toast.success("Producto creado exitosamente");
        } catch (error) {
            console.error("Error creating producto:", error);
            toast.error("Error al crear el producto");
            throw error;
        }
    };

    const handleEliminarProducto = async () => {
        if (!deletingProducto) return;
        try {
            await eliminarProducto(deletingProducto.id);
            setProductos((prev) => prev.filter((p) => p.id !== deletingProducto.id));
            toast.success("Producto eliminado exitosamente");
        } catch (error) {
            console.error("Error deleting producto:", error);
            toast.error("Error al eliminar el producto");
            throw error;
        }
    };

    const columns: Column<Producto>[] = [
        {
            header: "Producto",
            accessor: (producto) => {
                const cfg = tipoConfig(producto.tipo);
                return (
                    <div className="space-y-0.5">
                        <div className="flex items-center gap-2">
                            <div className={clsx("flex items-center justify-center w-8 h-8 rounded-lg", cfg.iconBg)}>
                                <cfg.Icon className={clsx("h-4 w-4", cfg.iconColor)} />
                            </div>
                            <div>
                                <div className="font-semibold text-gray-900 dark:text-gray-100 text-sm">{producto.nombre}</div>
                                <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
                                    <Tag className="h-3 w-3" />
                                    <span>{producto.codigo}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                );
            },
        },
        {
            header: "Tipo",
            accessor: (producto) => (
                <span className={clsx(
                    "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium capitalize",
                    tipoConfig(producto.tipo).badge
                )}>
                    {producto.tipo}
                </span>
            ),
            className: "w-[120px]",
        },
        {
            header: "Categoría",
            accessor: (producto) => (
                <span className="text-sm text-gray-600 dark:text-gray-400">
                    {producto.categoria || "—"}
                </span>
            ),
            className: "w-[120px]",
        },
        {
            header: "Precio",
            accessor: (producto) => (
                <div className="text-left">
                    <div className="font-semibold text-gray-900 dark:text-gray-100 text-sm">
                        {formatCurrency(producto.precio_unitario, producto.moneda)}
                    </div>
                    {producto.costo_unitario != null && producto.costo_unitario > 0 && (
                        <div className="text-xs text-gray-400 dark:text-gray-500">
                            Costo: {formatCurrency(producto.costo_unitario, producto.moneda)}
                        </div>
                    )}
                </div>
            ),
            className: "w-[140px] text-left",
        },
        {
            header: "Stock",
            accessor: (producto) => (
                <div className="text-left">
                    {producto.tiene_stock ? (
                        <span className={clsx(
                            "inline-flex items-center px-2.5 py-1 rounded text-xs font-medium",
                            producto.cantidad_stock > 10
                                ? "bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                                : producto.cantidad_stock > 0
                                    ? "bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                                    : "bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                        )}>
                            {producto.cantidad_stock}
                        </span>
                    ) : (
                        <span className="text-xs text-gray-400 dark:text-gray-500">N/A</span>
                    )}
                </div>
            ),
            className: "w-[120px] text-left",
        },
        {
            header: "Estado",
            accessor: (producto) => (
                <span className={clsx(
                    "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium",
                    producto.estado === "activo"
                        ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                        : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
                )}>
                    {producto.estado === "activo" ? "Activo" : "Inactivo"}
                </span>
            ),
            className: "w-[100px]",
        },
        {
            header: "",
            accessor: (producto) => (
                <div className="flex items-center gap-1">
                    <button
                        onClick={(e) => { e.stopPropagation(); handleEditarProducto(producto); }}
                        className="p-1.5 rounded-lg text-gray-500 hover:text-orange-600 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-colors"
                    >
                        <Pencil className="h-4 w-4" />
                    </button>
                    <button
                        onClick={(e) => { e.stopPropagation(); setDeletingProducto(producto); }}
                        className="p-1.5 rounded-lg text-gray-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                    >
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
                        Productos <span className="text-s text-gray-500 dark:text-gray-400">({productos.length})</span>
                    </h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-1">
                        Gestiona tu catálogo de productos y servicios.
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    {isAdmin && (
                        <button
                            onClick={() => setIsImportModalOpen(true)}
                            className="inline-flex items-center justify-center gap-2 rounded-xl border border-emerald-200 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-900/20 px-4 py-2 text-sm font-medium text-emerald-700 dark:text-emerald-400 hover:bg-emerald-100 dark:hover:bg-emerald-900/40 transition-all cursor-pointer"
                        >
                            <Upload className="h-4 w-4" />
                            Importar Excel
                        </button>
                    )}
                    <button
                        onClick={() => setIsCreateModalOpen(true)}
                        className="inline-flex items-center justify-center gap-2 rounded-xl bg-orange-600 px-4 py-2 text-sm font-medium text-white shadow-lg shadow-orange-500/20 hover:bg-orange-700 hover:shadow-orange-500/30 transition-all focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 cursor-pointer"
                    >
                        <Plus className="h-4 w-4" />
                        Nuevo Producto
                    </button>
                </div>
            </div>

            {/* Table Section */}
            <div className="space-y-4">
                <DataTable
                    columns={columns}
                    data={productos}
                    isLoading={isLoading}
                    searchable={true}
                    searchKeys={["nombre", "codigo", "categoria", "marca"]}
                />
            </div>

            {/* Edit Modal */}
            <EditModal<Producto>
                open={isEditModalOpen}
                onClose={() => { setIsEditModalOpen(false); setEditingProducto(null); }}
                title="Editar Producto"
                description="Modifica los datos del producto seleccionado."
                item={editingProducto}
                fields={productoFields}
                onSave={handleGuardarProducto}
            />

            {/* Create Modal */}
            <EditModal<Producto>
                open={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                mode="create"
                title="Nuevo Producto"
                description="Registra un nuevo producto o servicio en el catálogo."
                fields={productoFields.map((f) =>
                    f.key === "codigo" ? { ...f, readOnly: false } : f
                )}
                defaultValues={{
                    tipo: "producto",
                    moneda: "PEN",
                    unidad_medida: "UND",
                    aplica_igv: true,
                    igv_porcentaje: 18,
                    tipo_afectacion_igv: "10",
                    tiene_stock: false,
                    cantidad_stock: 0,
                    estado: "activo",
                } as Partial<Producto>}
                onSave={handleCrearNuevoProducto}
                submitLabel="Registrar Producto"
            />

            {/* Delete Confirm */}
            <ConfirmDialog
                open={!!deletingProducto}
                onClose={() => setDeletingProducto(null)}
                onConfirm={handleEliminarProducto}
                variant="destructive"
                title="Eliminar Producto"
                description={`¿Estás seguro de que deseas eliminar "${deletingProducto?.nombre}"? Esta acción no se puede deshacer.`}
                confirmLabel="Sí, eliminar"
            />

            {/* Import Modal */}
            <ImportModal
                open={isImportModalOpen}
                onClose={() => setIsImportModalOpen(false)}
                title="Importar Productos"
                entityName="productos"
                onDownloadTemplate={descargarPlantillaProductos}
                onImport={importarProductos}
                onSuccess={() => { toast.success("Productos importados"); fetchProductos(); }}
                templateFilename="plantilla_productos.xlsx"
            />
        </div>
    );
}
