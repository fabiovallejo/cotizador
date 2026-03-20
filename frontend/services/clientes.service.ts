import { apiFetch, apiFetchBlob } from "@/lib/api";
import type { Cliente } from "@/types/clientes";

export async function crearCliente(cliente: Cliente): Promise<Cliente> {
    return apiFetch<Cliente>("/clientes/crear", {
        method: "POST",
        body: JSON.stringify(cliente),
    });
}

export async function listarClientes(): Promise<Cliente[]> {
    return apiFetch<Cliente[]>("/clientes/listar?limit=5000")
}

export async function actualizarCliente(cliente: Cliente): Promise<Cliente> {
    return apiFetch<Cliente>(`/clientes/actualizar/${cliente.id}`, {
        method: "PUT",
        body: JSON.stringify(cliente),
    });
}

export async function eliminarCliente(id: number): Promise<void> {
    return apiFetch(`/clientes/eliminar/${id}`, {
        method: "DELETE",
    });
}

export async function descargarPlantillaClientes(): Promise<Blob> {
    return apiFetchBlob("/importacion/plantilla/clientes");
}

export async function importarClientes(file: File): Promise<{ creados: number; errores: { fila: number | string; error: string }[] }> {
    const formData = new FormData();
    formData.append("file", file);
    return apiFetch("/importacion/clientes", {
        method: "POST",
        body: formData,
    });
}
