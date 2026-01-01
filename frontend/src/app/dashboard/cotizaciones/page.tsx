"use client";

import { useEffect, useState } from "react";
import { listarCotizaciones } from "../../../services/cotizacionesService";
import { Cotizacion } from "../../../types/cotizacion";
import { useRouter } from "next/navigation";

export default function CotizacionesPage() {
  const router = useRouter();

  const [cotizaciones, setCotizaciones] = useState<Cotizacion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {

    const fetchData = async () => {
      try {
        const res = await listarCotizaciones();
        console.log("Respuesta API:", res);
        setCotizaciones(res.data);
      } catch {
        alert("Error cargando cotizaciones");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <p>Cargando...</p>;

  return (
    <div>
      <h1>Cotizaciones</h1>

      <button onClick={() => router.push("/dashboard/cotizaciones/nueva")}>
        Nueva cotización
      </button>

      <hr />

      {cotizaciones.length === 0 ? (
        <p>No hay cotizaciones</p>
      ) : (
        <ul>
          {cotizaciones.map(c => (
            <li
              key={c.id_cotizacion}
              onClick={() =>
                router.push(`/dashboard/cotizaciones/${c.id_cotizacion}`)
              }
              style={{ cursor: "pointer" }}
            >
              {c.codigo} – {c.estado} – S/. {c.total}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
