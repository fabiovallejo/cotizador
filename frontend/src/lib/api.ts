const API_URL = process.env.NEXT_PUBLIC_API_URL

export async function apiFetch(
  endpoint: string,
  options: RequestInit = {},
  token?: string
) {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` })
  }

  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers
  })

  const data = await res.json()

  if (!res.ok) {
    throw new Error(data.message || "Error en la API")
  }

  return data
}
