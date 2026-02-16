import { apiFetch } from "@/lib/api";

// ============================================================================
// TIPOS
// ============================================================================

export interface Alerta {
    tipo: "info" | "warning" | "danger";
    mensaje: string;
    producto?: string;
}

export interface MetricasCotizaciones {
    total_cotizaciones: number;
    monto_total: number;
    porcentaje_aceptadas: number;
    tasa_conversion: number;
    valor_promedio: number;
    tasa_rechazo: number;
    pendientes: number;
    monto_perdido: number;
}

export interface DetalleCotizacion {
    id: number;
    numero: string;
    cliente: string;
    vendedor: string;
    total: number;
    moneda: string;
    estado: string;
    fecha: string;
}

export interface ReporteCotizaciones {
    metricas: MetricasCotizaciones;
    alertas: Alerta[];
    detalle: DetalleCotizacion[];
}

export interface ProductoTop {
    id: number;
    codigo: string;
    nombre: string;
    cantidad_vendida: number;
    ingresos: number;
    porcentaje_total: number;
    margen: number | null;
    tasa_conversion: number;
    total_cotizaciones: number;
    cotizaciones_cerradas: number;
    monto_no_cerrado: number;
}

export interface ReporteProductosTop {
    total_ingresos: number;
    total_productos: number;
    productos: ProductoTop[];
    alertas: Alerta[];
}

export interface ClienteReporte {
    id: number;
    razon_social: string;
    numero_documento: string;
    tipo_documento: string;
    total_cotizaciones: number;
    aceptadas: number;
    monto_total: number;
    ticket_promedio: number;
    ultima_cotizacion: string;
    segmento: "VIP" | "Regular";
    dias_inactivo: number | null;
    monto_historico: number;
    es_inactivo: boolean;
}

export interface ReporteClientes {
    total_clientes: number;
    promedio_global: number;
    umbral_vip: number;
    inactivos: number;
    clientes: ClienteReporte[];
    alertas: Alerta[];
}

// ============================================================================
// API CALLS
// ============================================================================

export async function obtenerReporteCotizaciones(
    fechaInicio: string,
    fechaFin: string,
    vendedorId?: number,
    clienteId?: number
): Promise<ReporteCotizaciones> {
    let url = `/reportes/cotizaciones?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`;
    if (vendedorId) url += `&vendedor_id=${vendedorId}`;
    if (clienteId) url += `&cliente_id=${clienteId}`;
    return apiFetch<ReporteCotizaciones>(url);
}

export async function obtenerReporteProductosTop(
    fechaInicio: string,
    fechaFin: string,
): Promise<ReporteProductosTop> {
    return apiFetch<ReporteProductosTop>(
        `/reportes/productos-top?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`
    );
}

export async function obtenerReporteClientes(
    fechaInicio: string,
    fechaFin: string,
): Promise<ReporteClientes> {
    return apiFetch<ReporteClientes>(
        `/reportes/clientes?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`
    );
}
