export interface Cotizacion {
  id_cotizacion: number;
  codigo: string;
  estado: string;
  subtotal: number;
  total: number;
}

export interface CotizacionItem {
  id_producto: number;
  nombre_producto: string;
  precio_unitario: number;
  cantidad: number;
  subtotal: number;
}

export interface CotizacionDetalle {
  id_cotizacion: number;
  codigo: string;
  estado: string;
  subtotal: number;
  total: number;
  items: CotizacionItem[];
}