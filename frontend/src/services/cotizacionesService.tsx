import { apiFetch } from "./api";
import { apiFetchBlob } from "./apiBinary";

export function obtenerCotizaciones() {
  return apiFetch("/cotizaciones/");
}

export function crearCotizacion(id_cliente: number) {
  return apiFetch("/cotizaciones/", {
    method: "POST",
    body: JSON.stringify({ id_cliente })
  });
}

export async function listarCotizaciones() {
  return apiFetch("/cotizaciones/", {
    method: "GET"
  });
}

export async function obtenerCotizacion(id: number) {
  return apiFetch(`/cotizaciones/${id}`, {
    method: "GET"
  });
}

export async function descargarPdfCotizacion(id: number) {
  return apiFetchBlob(`/cotizaciones/${id}/pdf`);
}

export async function cerrarCotizacion(id: number) {
  return apiFetch(`/cotizaciones/${id}/cerrar`, {
    method: "PUT",
  });
}

export async function agregarItemCotizacion(
  idCotizacion: number,
  idProducto: number,
  cantidad: number
) {
  return apiFetch(`/cotizaciones/${idCotizacion}/items`, {
    method: "POST",
    body: JSON.stringify({
      id_producto: idProducto,
      cantidad,
    }),
  });
}

export async function eliminarCotizacion(id: number) {
  return apiFetch(`/cotizaciones/${id}`, {
    method: "DELETE",
  });
}