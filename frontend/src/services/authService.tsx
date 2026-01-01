const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000/api/v1";

interface LoginResponse {
  success: boolean;
  access_token: string;
}

export async function loginRequest(email: string, password: string) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ email, password })
  });

  if (!res.ok) {
    throw new Error("Credenciales inválidas");
  }

  const data: LoginResponse = await res.json();
  return data;
}
