import { apiFetch } from "./api"
import { LoginResponse } from "../types/auth"

export async function login(email: string, password: string) {
  const data: LoginResponse = await apiFetch(
    "/api/v1/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ email, password })
    }
  )

  localStorage.setItem("token", data.access_token)
  return data
}

export function logout() {
  localStorage.removeItem("token")
}

export function getToken() {
  if (typeof window === "undefined") return null
  return localStorage.getItem("token")
}
