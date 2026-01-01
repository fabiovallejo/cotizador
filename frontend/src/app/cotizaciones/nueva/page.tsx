"use client";

import { useState } from "react";
import {crearCotizacion, agregarItemCotizacion} from "../../../services/cotizacionesService";
import { useRouter } from "next/navigation";

type ItemDraft = {
  idProducto: number;
  nombre: string;
  precio: number;
  cantidad: number;
};

export default function NuevaCotizacionPage() {
  const router = useRouter();

  const [idCliente, setIdCliente] = useState<number | null>(null);
  const [items, setItems] = useState<ItemDraft[]>([]);

  const [idProducto, setIdProducto] = useState<number | null>(null);
  const [cantidad, setCantidad] = useState<number>(1);

  function agregarAlCarrito() {
    if (!idProducto || cantidad <= 0) {
      alert("Producto y cantidad inválidos");
      return;
    }

    const producto = {
      id: idProducto,
      nombre: `Producto ${idProducto}`,
      precio: 0
    };

    setItems(prev => {
      const idx = prev.findIndex(x => x.idProducto === producto.id);
      if (idx !== -1) {
        const copy = [...prev];
        copy[idx] = {
          ...copy[idx],
          cantidad: copy[idx].cantidad + cantidad
        };
        return copy;
      }

      return [
        ...prev,
        {
          idProducto: producto.id,
          nombre: producto.nombre,
          precio: producto.precio,
          cantidad
        }
      ];
    });

    setCantidad(1);
  }

  const puedeCrear = idCliente !== null && items.length > 0;

  async function handleCrearCotizacion() {
    if (!idCliente || items.length === 0) return;

    try {
      const res = await crearCotizacion(idCliente);
      const idCotizacion =
        res.data.id_cotizacion ?? res.data.id;

      for (const it of items) {
        await agregarItemCotizacion(
          idCotizacion,
          it.idProducto,
          it.cantidad
        );
      }

      router.push(`/dashboard/cotizaciones/${idCotizacion}`);
    } catch (e: any) {
      alert(e.message || "Error creando la cotización");
    }
  }

  return (
    <div>
      <h1>Nueva Cotización</h1>

      <div>
        <input
          type="number"
          placeholder="ID Cliente"
          value={idCliente ?? ""}
          onChange={e => setIdCliente(Number(e.target.value))}
        />
      </div>

      <hr />

      <h3>Agregar ítem</h3>

      <input
        type="number"
        placeholder="ID Producto"
        value={idProducto ?? ""}
        onChange={e => setIdProducto(Number(e.target.value))}
      />

      <input
        type="number"
        min={1}
        value={cantidad}
        onChange={e => setCantidad(Number(e.target.value))}
      />

      <button onClick={agregarAlCarrito}>
        Agregar ítem
      </button>

      <ul>
        {items.map((it, idx) => (
          <li key={idx}>
            {it.nombre} – Cantidad: {it.cantidad}
          </li>
        ))}
      </ul>

      {items.length === 0 && (
        <p>Agrega al menos un ítem para crear la cotización.</p>
      )}

      <button disabled={!puedeCrear} onClick={handleCrearCotizacion}>
        Crear cotización
      </button>
    </div>
  );
}
