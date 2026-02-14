export interface Cotizacion {
    id: number;
    numero_cotizacion: string;
    cliente_id: number;
    usuario_id: number;
    moneda: string;
    tipo_cambio?: number;
    subtotal: number;
    descuento_total: number;
    igv_total: number;
    total: number;
    estado: string;
    vigencia_dias: number;
    fecha_vencimiento?: string;
    notas_internas?: string;
    terminos_condiciones?: string;
    forma_pago?: string;
    lugar_entrega?: string;
    tiempo_entrega?: string;
    convertida_a_factura_id?: number;
    created_at?: string;
}

export interface ItemCotizacion {
    id: number;
    cotizacion_id: number;
    producto_id: number;
    cantidad: number;
    precio_unitario: number;
    igv_porcentaje: number;
    igv_monto: number;
    subtotal: number;
    total: number;
    orden_item?: number;
    created_at?: string;
}

export interface CreateItemCotizacionRequest {
    producto_id: number;
    cantidad: number;
}

export interface CreateCotizacionRequest {
    cliente_id: number;
    moneda: string;
    vigencia_dias: number;
    notas_internas?: string;
    terminos_condiciones?: string;
    forma_pago?: string;
    lugar_entrega?: string;
    tiempo_entrega?: string;
    items: CreateItemCotizacionRequest[];
}
