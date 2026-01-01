"use client";

import { useEffect, useState } from "react";
import { obtenerCotizaciones } from "../../services/cotizacionesService";

export default function CotizacionesPage() {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    obtenerCotizaciones().then(res => {
      setData(res.data);
    });
  }, []);

  return (
    <div>
      <h1>Cotizaciones</h1>

      {data.map(c => (
        <div key={c.id_cotizacion}>
          <p>{c.codigo}</p>
          <p>{c.estado}</p>
        </div>
      ))}
    </div>
  );
}
