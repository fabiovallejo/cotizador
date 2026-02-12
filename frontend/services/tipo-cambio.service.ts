import { apiFetch } from "@/lib/api";

export interface TipoCambio {
    fecha: string;
    compra: string;
    venta: string;
}

/**
 * Obtiene el tipo de cambio del día desde SUNAT (vía backend).
 */
export async function obtenerTipoCambio(): Promise<TipoCambio> {
    return apiFetch<TipoCambio>("/utils/tipo-cambio");
}
