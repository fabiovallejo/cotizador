export interface Producto {
    id: number;
    codigo: string;
    nombre: string;
    descripcion?: string;
    codigo_unspsc?: string;
    tipo: string;
    categoria?: string;
    marca?: string;
    precio_unitario: number;
    costo_unitario?: number;
    precio_distribuidor?: number;
    aplica_igv: boolean;
    igv_porcentaje: number;
    tipo_afectacion_igv: string;
    moneda: string;
    unidad_medida: string;
    tiene_stock: boolean;
    cantidad_stock: number;
    estado: string;
    created_at?: string;
    updated_at?: string;
}
