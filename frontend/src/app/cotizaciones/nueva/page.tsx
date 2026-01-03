"use client";

import { useState } from "react";
import {crearCotizacion, agregarItemCotizacion} from "../../../services/cotizacionesService";
import { buscarProductos } from "../../../services/productosService";
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

  const [cantidad, setCantidad] = useState<number>(1);
  const [query, setQuery] = useState("");
  const [resultados, setResultados] = useState<any[]>([]);
  const [loadingProductos, setLoadingProductos] = useState(false);

  function agregarAlCarrito(
    producto: { id: number; nombre: string; precio: number },
    cantidadAgregar: number
  ) {
    if (!producto?.id || cantidadAgregar <= 0) {
      alert("Producto y cantidad inválidos");
      return;
    }

    setItems(prev => {
      const idx = prev.findIndex(x => x.idProducto === producto.id);

      if (idx !== -1) {
        const copy = [...prev];
        copy[idx] = {
          ...copy[idx],
          cantidad: copy[idx].cantidad + cantidadAgregar
        };
        return copy;
      }

      return [
        ...prev,
        {
          idProducto: producto.id,
          nombre: producto.nombre,
          precio: producto.precio,
          cantidad: cantidadAgregar
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

  function eliminarItem(idProducto: number) {
    setItems(prev => prev.filter(it => it.idProducto !== idProducto));
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
        placeholder="Buscar producto"
        value={query}
        onChange={e => setQuery(e.target.value)}
      />

      <button
        onClick={async () => {
          if (query.trim().length < 2) {
            alert("Escribe al menos 2 caracteres");
            return;
          }

          setLoadingProductos(true);
          try {
            const res = await buscarProductos(query);
            setResultados(res.data);
          } catch (err: any) {
            console.error("Error buscar productos:", err);
            alert(err.message || "Error buscando productos");
          } finally {
            setLoadingProductos(false);
          }
        }}
      >
        Buscar
      </button>

      <ul>
        {resultados.map(p => (
          <li key={p.id_producto}>
            {p.nombre} – S/. {p.precio}
            <button
              onClick={() => {
                agregarAlCarrito(
                  { id: p.id_producto, nombre: p.nombre, precio: p.precio },
                  cantidad
                );
                setResultados([]);
                setQuery("");
              }}
            >
              Agregar
            </button>
          </li>
        ))}
      </ul>

      <ul>
        {items.map(it => (
          <li key={it.idProducto}>
            {it.nombre}

            <input
              type="number"
              min={1}
              value={it.cantidad}
              onChange={e => {
                const nuevaCantidad = Number(e.target.value);
                if (nuevaCantidad <= 0) return;
                setItems(prev =>
                  prev.map(item =>
                    item.idProducto === it.idProducto
                      ? { ...item, cantidad: nuevaCantidad }
                      : item
                  )
                );
              }}
              style={{ width: "60px", marginLeft: "10px" }}
            />

            <button
              onClick={() => eliminarItem(it.idProducto)}
              style={{ marginLeft: "10px", color: "red" }}
            >
              Eliminar
            </button>
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
