import { apiFetch, apiFetchBlob } from "@/lib/api";
import type {
    Cotizacion,
    ItemCotizacion,
    CreateCotizacionRequest,
} from "@/types/cotizaciones";

export async function crearCotizacion(data: CreateCotizacionRequest): Promise<Cotizacion> {
    return apiFetch<Cotizacion>("/cotizaciones/crear", {
        method: "POST",
        body: JSON.stringify(data),
    });
}

export async function listarCotizaciones(params?: {
    busqueda?: string;
    estado?: string;
    usuario_id?: number;
}): Promise<Cotizacion[]> {
    const searchParams = new URLSearchParams();
    if (params?.busqueda) searchParams.set("busqueda", params.busqueda);
    if (params?.estado) searchParams.set("estado", params.estado);
    if (params?.usuario_id) searchParams.set("usuario_id", String(params.usuario_id));
    const qs = searchParams.toString();
    return apiFetch<Cotizacion[]>(`/cotizaciones/listar${qs ? `?${qs}` : ""}`);
}

export async function obtenerCotizacion(id: number): Promise<Cotizacion> {
    return apiFetch<Cotizacion>(`/cotizaciones/${id}`);
}

export async function obtenerItemsCotizacion(id: number): Promise<ItemCotizacion[]> {
    return apiFetch<ItemCotizacion[]>(`/cotizaciones/${id}/items`);
}

export async function editarCotizacion(id: number, data: CreateCotizacionRequest): Promise<Cotizacion> {
    return apiFetch<Cotizacion>(`/cotizaciones/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
}

export async function eliminarCotizacion(id: number): Promise<void> {
    await apiFetch(`/cotizaciones/${id}`, {
        method: "DELETE",
    });
}

export async function descargarPdfCotizacion(id: number): Promise<void> {
    const blob = await apiFetchBlob(`/cotizaciones/${id}/pdf`);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `cotizacion-${id}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
}

export async function cambiarEstadoCotizacion(id: number, estado: string): Promise<Cotizacion> {
    return apiFetch<Cotizacion>(`/cotizaciones/${id}/estado`, {
        method: "PATCH",
        body: JSON.stringify({ estado }),
    });
}
