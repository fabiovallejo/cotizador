import { apiFetch, apiFetchBlob } from "@/lib/api";
import type { Producto } from "@/types/productos";

export async function crearProducto(producto: Producto): Promise<Producto> {
    return apiFetch<Producto>("/productos/crear", {
        method: "POST",
        body: JSON.stringify(producto),
    });
}

export async function listarProductos(): Promise<Producto[]> {
    return apiFetch<Producto[]>("/productos/listar?limit=5000");
}

export async function actualizarProducto(producto: Producto): Promise<Producto> {
    return apiFetch<Producto>(`/productos/actualizar/${producto.id}`, {
        method: "PUT",
        body: JSON.stringify(producto),
    });
}

export async function eliminarProducto(id: number): Promise<void> {
    return apiFetch(`/productos/eliminar/${id}`, {
        method: "DELETE",
    });
}

export async function descargarPlantillaProductos(): Promise<Blob> {
    return apiFetchBlob("/importacion/plantilla/productos");
}

export async function importarProductos(file: File): Promise<{ creados: number; errores: { fila: number | string; error: string }[] }> {
    const formData = new FormData();
    formData.append("file", file);
    return apiFetch("/importacion/productos", {
        method: "POST",
        body: formData,
    });
}

