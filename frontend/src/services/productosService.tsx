import { apiFetch } from "./api";

export async function buscarProductos(search: string) {
  return apiFetch(`/productos/?search=${encodeURIComponent(search)}`);
}

