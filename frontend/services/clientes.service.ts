import { apiFetch } from "@/lib/api";
import type { Cliente } from "@/types/clientes";

export async function crearCliente(cliente: Cliente): Promise<Cliente> {
    return apiFetch<Cliente>("/clientes/crear", {
        method: "POST",
        body: JSON.stringify(cliente),
    });
}

export async function listarClientes(): Promise<Cliente[]> {
    return apiFetch<Cliente[]>("/clientes/listar")
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