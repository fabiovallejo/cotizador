"use client";

import { useState } from "react";
import { crearCotizacion } from "../../../services/cotizacionesService";
import { useRouter } from "next/navigation";

export default function NuevaCotizacionPage() {
  const [idCliente, setIdCliente] = useState("");
  const router = useRouter();

  const crear = async () => {
    const res = await crearCotizacion(Number(idCliente));
    router.push(`/cotizaciones/${res.data.id_cotizacion}`);
  };

  return (
    <div>
      <h1>Nueva Cotización</h1>

      <input
        placeholder="ID Cliente"
        value={idCliente}
        onChange={e => setIdCliente(e.target.value)}
      />

      <button onClick={crear}>Crear</button>
    </div>
  );
}
