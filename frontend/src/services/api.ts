const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000/api/v1";

export async function apiFetch(endpoint: string, options?: RequestInit) {
  const token = localStorage.getItem("token");

  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.message || "ERROR EN LA API");
  }

  return data;
}
