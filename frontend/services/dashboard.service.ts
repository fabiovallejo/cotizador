import { apiFetch } from "@/lib/api";

// ============================================================================
// TIPOS
// ============================================================================

export interface DashboardKPIs {
    cotizaciones: {
        valor: number;
        variacion: number;
    };
    tasa_conversion: {
        valor: number;
        aceptadas: number;
        total: number;
        variacion: number;
    };
    ingresos_pen: {
        valor: number;
        variacion: number;
        ticket_promedio: number;
    };
    ingresos_usd: {
        valor: number;
        variacion: number;
        ticket_promedio: number;
    };
    alertas: {
        pendientes: number;
        inactivos: number;
    };
}

export interface CotizacionPendiente {
    id: number;
    numero: string;
    cliente: string;
    monto: number;
    dias: number;
    fecha: string;
    vendedor: string;
    estado: string;
}

export interface SerieDiaria {
    dia: string;
    total: number;
    aceptadas: number;
}

export interface ProductoDashboard {
    id: number;
    codigo: string;
    nombre: string;
    cantidad: number;
    ingresos: number;
    tasa_conversion: number;
    cotizaciones_total: number;
    cotizaciones_cerradas: number;
    monto_perdido: number;
}

export interface ClienteInactivo {
    id: number;
    razon_social: string;
    ultima_cotizacion: string;
    dias: number;
    monto_historico: number;
}

export interface VendedorDashboard {
    id: number;
    nombre: string;
    cotizaciones: number;
    cerradas: number;
    tasa_conversion: number;
    monto: number;
}

export interface DashboardData {
    periodo_dias: number;
    kpis: DashboardKPIs;
    cotizaciones_pendientes: CotizacionPendiente[];
    serie_diaria: SerieDiaria[];
    top_productos: ProductoDashboard[];
    productos_problematicos: ProductoDashboard[];
    clientes_inactivos: ClienteInactivo[];
    top_vendedores: VendedorDashboard[];
}

// ============================================================================
// API CALL
// ============================================================================

export async function obtenerDashboard(
    periodo: number = 30
): Promise<DashboardData> {
    return apiFetch<DashboardData>(
        `/reportes/dashboard?periodo=${periodo}`
    );
}
