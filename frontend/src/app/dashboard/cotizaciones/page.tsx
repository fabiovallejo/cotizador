"use client";

import { useEffect, useState } from "react";
import { listarCotizaciones, descargarPdfCotizacion, cerrarCotizacion } from "../../../services/cotizacionesService";
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
            <li key={c.id_cotizacion}>
              {c.codigo} – {c.estado} – S/. {c.total}
              <button className="hover:cursor-pointer ml-7 my-4 p-3 bg-white rounded-[5px] text-black" onClick={() => router.push(`/dashboard/cotizaciones/${c.id_cotizacion}`)
              }>Ver Detalles</button>
              <button className=" ml-7 my-4 p-3 bg-white rounded-[5px] text-black hover:cursor-pointer"   
              onClick={async () => {
                try {
                  const blob = await descargarPdfCotizacion(c.id_cotizacion);
                  const url = window.URL.createObjectURL(blob);

                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `cotizacion-${c.id_cotizacion}.pdf`;
                  document.body.appendChild(a);
                  a.click();

                  a.remove();
                  window.URL.revokeObjectURL(url);
                } catch {
                  alert("Error al descargar el PDF");
                }
              }}>Descargar PDF</button>
              {c.estado === "BORRADOR" && (
              <button className="hover:cursor-pointer ml-7 my-4 p-3 bg-white rounded-[5px] text-black"
              onClick={async () => {
                if (!confirm("¿Cerrar esta cotización?")) return;

                await cerrarCotizacion(c.id_cotizacion);
                router.refresh();}}>Cerrar Cotizacion</button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
