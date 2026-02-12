export interface Cliente {
    id: number;
    tipo_documento: string;
    numero_documento: string;
    razon_social: string;
    nombre_comercial?: string;
    email?: string;
    telefono?: string;
    direccion_completa?: string;
    ubigeo?: string;
    es_cliente_frecuente: boolean;
    estado: string;
    created_at?: string;
    updated_at?: string;
}