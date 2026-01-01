import { logout } from "../lib/auth";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000/api/v1";

export async function apiFetchBlob(endpoint: string) {
  const token = localStorage.getItem("token");

  const res = await fetch(`${API_URL}${endpoint}`, {
    method: "GET",
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  });

  if (res.status === 401) {
    logout();
    throw new Error("Sesión expirada");
  }

  if (res.status === 403) {
    throw new Error("No tienes permisos");
  }

  if (!res.ok) {
    throw new Error("Error al descargar archivo");
  }

  return res.blob();
}
