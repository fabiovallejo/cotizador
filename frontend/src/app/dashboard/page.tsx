"use client";

import { useAuth } from "../../context/AuthContext";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const { logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <div>
      <h1>Dashboard</h1>

      <button onClick={() => router.push("/cotizaciones/nueva")}>
        Nueva cotización
      </button>

      <button onClick={handleLogout}>Cerrar sesión</button>
    </div>
  );
}
