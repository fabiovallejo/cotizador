"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { obtenerCotizacion } from "../../../../services/cotizacionesService";
import { CotizacionDetalle } from "../../../../types/cotizacion";
import { useAuth } from "../../../../context/AuthContext";

export default function CotizacionDetallePage() {
  const { id } = useParams();
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  const [cotizacion, setCotizacion] = useState<CotizacionDetalle | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }

    const fetchData = async () => {
      try {
        const res = await obtenerCotizacion(Number(id));
        setCotizacion(res.data);
      } catch {
        alert("Error cargando cotización");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, isAuthenticated, router]);

  if (loading) return <p>Cargando...</p>;
  if (!cotizacion) return <p>No encontrada</p>;

  return (
    <div>
      <h1>{cotizacion.codigo}</h1>
      <p>Estado: {cotizacion.estado}</p>
      <p>Total: S/. {cotizacion.total}</p>

      <h2>Items</h2>

      {cotizacion.items.length === 0 ? (
        <p>Sin items</p>
      ) : (
        <ul>
          {cotizacion.items.map((item, index) => (
            <li key={index}>
              {item.nombre_producto} – {item.cantidad} × {item.precio_unitario}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
