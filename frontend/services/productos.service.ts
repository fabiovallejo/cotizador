import { apiFetch } from "@/lib/api";
import type { Producto } from "@/types/productos";

export async function crearProducto(producto: Producto): Promise<Producto> {
    return apiFetch<Producto>("/productos/crear", {
        method: "POST",
        body: JSON.stringify(producto),
    });
}

export async function listarProductos(): Promise<Producto[]> {
    return apiFetch<Producto[]>("/productos/listar");
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
