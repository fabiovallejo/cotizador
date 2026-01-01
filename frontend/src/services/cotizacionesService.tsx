import { apiFetch } from "./api";

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