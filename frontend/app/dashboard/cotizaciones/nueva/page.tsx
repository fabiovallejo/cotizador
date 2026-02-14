"use client";

import { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { listarClientes } from "@/services/clientes.service";
import { listarProductos } from "@/services/productos.service";
import { crearCotizacion } from "@/services/cotizaciones.service";
import { obtenerTipoCambio, type TipoCambio } from "@/services/tipo-cambio.service";
import type { Cliente } from "@/types/clientes";
import type { Producto } from "@/types/productos";
import type { CreateCotizacionRequest } from "@/types/cotizaciones";
import {
    ArrowLeft,
    ArrowRightLeft,
    Search,
    Plus,
    Minus,
    Trash2,
    ShoppingCart,
    Loader2,
    Package,
    Wrench,
    Layers,
} from "lucide-react";
import Link from "next/link";

import { clsx } from "clsx";

/* ── Cart item type ── */
interface CartItem {
    producto: Producto;
    cantidad: number;
}

/* ── Helpers ── */
const formatCurrency = (value: number, moneda: string) => {
    const symbol = moneda === "USD" ? "$" : "S/";
    return `${symbol} ${Number(value).toFixed(2)}`;
};

const tipoIcon = (tipo: string) => {
    if (tipo === "servicio") return Wrench;
    if (tipo === "combo") return Layers;
    return Package;
};

const tipoColor = (tipo: string) => {
    if (tipo === "servicio") return "text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20";
    if (tipo === "combo") return "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20";
    return "text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20";
};

export default function NuevaCotizacionPage() {
    const router = useRouter();

    /* ── Data loading ── */
    const [clientes, setClientes] = useState<Cliente[]>([]);
    const [productos, setProductos] = useState<Producto[]>([]);
    const [isLoadingData, setIsLoadingData] = useState(true);

    /* ── Form state ── */
    const [clienteId, setClienteId] = useState<number | "">("");
    const [moneda, setMoneda] = useState("PEN");
    const [vigenciaDias, setVigenciaDias] = useState(30);
    const [notasInternas, setNotasInternas] = useState("");
    const [terminosCondiciones, setTerminosCondiciones] = useState("");
    const [formaPago, setFormaPago] = useState("");
    const [lugarEntrega, setLugarEntrega] = useState("");
    const [tiempoEntrega, setTiempoEntrega] = useState("");

    /* ── Cart ── */
    const [cart, setCart] = useState<CartItem[]>([]);
    const [productSearch, setProductSearch] = useState("");
    const [showProductDropdown, setShowProductDropdown] = useState(false);

    /* ── Client search ── */
    const [clientSearch, setClientSearch] = useState("");
    const [showClientDropdown, setShowClientDropdown] = useState(false);

    /* ── Submitting ── */
    const [isSubmitting, setIsSubmitting] = useState(false);

    /* ── Exchange rate ── */
    const [tipoCambio, setTipoCambio] = useState<TipoCambio | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [cliData, prodData] = await Promise.all([
                    listarClientes(),
                    listarProductos(),
                ]);
                setClientes(cliData.filter((c) => c.estado === "activo"));
                setProductos(prodData.filter((p) => p.estado === "activo"));
                // Fetch exchange rate
                try {
                    const tc = await obtenerTipoCambio();
                    setTipoCambio(tc);
                } catch (err) {
                    console.error("Error fetching exchange rate:", err);
                }
            } catch (error) {
                console.error("Error loading data:", error);

            } finally {
                setIsLoadingData(false);
            }
        };
        fetchData();
    }, []);

    /* ── Filtered products ── */
    const filteredProducts = useMemo(() => {
        if (!productSearch.trim()) return [];
        const q = productSearch.toLowerCase();
        return productos
            .filter(
                (p) =>
                    p.nombre.toLowerCase().includes(q) ||
                    p.codigo.toLowerCase().includes(q)
            )
            .filter((p) => !cart.some((ci) => ci.producto.id === p.id))
            .slice(0, 8);
    }, [productSearch, productos, cart]);

    /* ── Filtered clients ── */
    const filteredClients = useMemo(() => {
        if (!clientSearch.trim()) return clientes.slice(0, 8);
        const q = clientSearch.toLowerCase();
        return clientes
            .filter(
                (c) =>
                    c.razon_social.toLowerCase().includes(q) ||
                    c.numero_documento.includes(q)
            )
            .slice(0, 8);
    }, [clientSearch, clientes]);

    /* ── Selected client name ── */
    const selectedClientName = useMemo(() => {
        if (!clienteId) return "";
        return clientes.find((c) => c.id === clienteId)?.razon_social ?? "";
    }, [clienteId, clientes]);

    /* ── Cart operations ── */
    const addToCart = (producto: Producto) => {
        setCart((prev) => [...prev, { producto, cantidad: 1 }]);
        setProductSearch("");
        setShowProductDropdown(false);
    };

    const updateQuantity = (productoId: number, delta: number) => {
        setCart((prev) =>
            prev.map((ci) =>
                ci.producto.id === productoId
                    ? { ...ci, cantidad: Math.max(1, ci.cantidad + delta) }
                    : ci
            )
        );
    };

    const setQuantity = (productoId: number, value: number) => {
        setCart((prev) =>
            prev.map((ci) =>
                ci.producto.id === productoId
                    ? { ...ci, cantidad: Math.max(1, value) }
                    : ci
            )
        );
    };

    const removeFromCart = (productoId: number) => {
        setCart((prev) => prev.filter((ci) => ci.producto.id !== productoId));
    };

    /* ── Check if mixed currencies ── */
    const hasMixedCurrencies = useMemo(() => {
        return cart.some((ci) => (ci.producto.moneda || "PEN") !== moneda);
    }, [cart, moneda]);

    /* ── Get exchange rate value for conversions ── */
    const tcVenta = useMemo(() => {
        if (!tipoCambio) return null;
        return parseFloat(tipoCambio.venta);
    }, [tipoCambio]);

    /* ── Convert a product price to the cotización currency ── */
    const convertPrice = (precioOriginal: number, monedaProducto: string): number => {
        const mp = monedaProducto || "PEN";
        if (mp === moneda) return precioOriginal;
        if (!tcVenta) return precioOriginal; // no TC available, show original
        if (moneda === "PEN") {
            // Product is USD, cotización is PEN → multiply
            return precioOriginal * tcVenta;
        } else {
            // Product is PEN, cotización is USD → divide
            return precioOriginal / tcVenta;
        }
    };

    /* ── Totals with live conversion ── */
    const { subtotal, igvTotal, total } = useMemo(() => {
        let sub = 0;
        let igv = 0;
        cart.forEach((ci) => {
            const convertedPrice = convertPrice(ci.producto.precio_unitario, ci.producto.moneda);
            const itemSub = convertedPrice * ci.cantidad;
            const itemIgv =
                itemSub * ((ci.producto.igv_porcentaje ?? 18) / 100);
            sub += itemSub;
            igv += itemIgv;
        });
        return { subtotal: sub, igvTotal: igv, total: sub + igv };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [cart, moneda, tcVenta]);

    /* ── Submit ── */
    const handleSubmit = async () => {
        if (!clienteId) {
            alert("Selecciona un cliente");
            return;
        }
        if (cart.length === 0) {
            alert("Agrega al menos un producto");
            return;
        }

        setIsSubmitting(true);
        try {
            const payload: CreateCotizacionRequest = {
                cliente_id: clienteId as number,
                moneda,
                vigencia_dias: vigenciaDias,
                notas_internas: notasInternas || undefined,
                terminos_condiciones: terminosCondiciones || undefined,
                forma_pago: formaPago || undefined,
                lugar_entrega: lugarEntrega || undefined,
                tiempo_entrega: tiempoEntrega || undefined,
                items: cart.map((ci) => ({
                    producto_id: ci.producto.id,
                    cantidad: ci.cantidad,
                })),
            };

            await crearCotizacion(payload);

            router.push("/dashboard/cotizaciones");
        } catch (error) {
            console.error("Error creating cotizacion:", error);

        } finally {
            setIsSubmitting(false);
        }
    };

    if (isLoadingData) {
        return (
            <div className="p-6 md:p-8 max-w-5xl mx-auto">
                <div className="flex items-center gap-3">
                    <Loader2 className="h-5 w-5 animate-spin text-orange-600" />
                    <span className="text-gray-500 dark:text-gray-400">
                        Cargando datos...
                    </span>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 md:p-8 max-w-5xl mx-auto space-y-8">
            {/* ── Header ── */}
            <div className="flex items-center gap-4">
                <Link
                    href="/dashboard/cotizaciones"
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                    <ArrowLeft className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                </Link>
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
                        Nueva Cotización
                    </h1>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                        Crea una propuesta comercial para tu cliente.
                    </p>
                </div>
            </div>

            {/* ── Configuration row ── */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Client selector */}
                <div className="relative md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                        Cliente <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                        <input
                            type="text"
                            value={
                                showClientDropdown
                                    ? clientSearch
                                    : selectedClientName
                            }
                            onChange={(e) => {
                                setClientSearch(e.target.value);
                                setShowClientDropdown(true);
                            }}
                            onFocus={() => {
                                setShowClientDropdown(true);
                                setClientSearch("");
                            }}
                            placeholder="Buscar cliente por nombre o documento..."
                            className="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-4 py-2.5 text-sm outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all"
                        />
                        <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                    </div>
                    {showClientDropdown && filteredClients.length > 0 && (
                        <div className="absolute z-20 mt-1 w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-xl max-h-60 overflow-y-auto">
                            {filteredClients.map((c) => (
                                <button
                                    key={c.id}
                                    type="button"
                                    onClick={() => {
                                        setClienteId(c.id);
                                        setClientSearch("");
                                        setShowClientDropdown(false);
                                    }}
                                    className={clsx(
                                        "w-full text-left px-4 py-3 text-sm hover:bg-orange-50 dark:hover:bg-orange-900/10 transition-colors border-b border-gray-100 dark:border-gray-800 last:border-0",
                                        clienteId === c.id &&
                                        "bg-orange-50 dark:bg-orange-900/10"
                                    )}
                                >
                                    <div className="font-medium text-gray-900 dark:text-gray-100">
                                        {c.razon_social}
                                    </div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">
                                        {c.tipo_documento}: {c.numero_documento}
                                    </div>
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Moneda + Vigencia */}
                <div className="grid grid-cols-2 gap-3">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                            Moneda
                        </label>
                        <select
                            value={moneda}
                            onChange={(e) => setMoneda(e.target.value)}
                            className="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2.5 text-sm outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all"
                        >
                            <option value="PEN">PEN</option>
                            <option value="USD">USD</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                            Vigencia
                        </label>
                        <div className="flex items-center gap-1.5">
                            <input
                                type="number"
                                min={1}
                                max={365}
                                value={vigenciaDias}
                                onChange={(e) =>
                                    setVigenciaDias(
                                        Math.max(1, Number(e.target.value))
                                    )
                                }
                                className="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2.5 text-sm outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all"
                            />
                            <span className="text-xs text-gray-400 whitespace-nowrap">
                                días
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* ── Product search + Cart ── */}
            <div className="rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/50 shadow-sm overflow-hidden">
                {/* Product search bar */}
                <div className="p-4 border-b border-gray-200 dark:border-gray-800">
                    <div className="relative">
                        <input
                            type="text"
                            value={productSearch}
                            onChange={(e) => {
                                setProductSearch(e.target.value);
                                setShowProductDropdown(true);
                            }}
                            onFocus={() => setShowProductDropdown(true)}
                            placeholder="Buscar producto por nombre o código..."
                            className="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 pl-10 pr-4 py-2.5 text-sm outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all"
                        />
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />

                        {/* Product dropdown */}
                        {showProductDropdown && filteredProducts.length > 0 && (
                            <div className="absolute z-20 mt-1 w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-xl max-h-72 overflow-y-auto">
                                {filteredProducts.map((p) => {
                                    const Icon = tipoIcon(p.tipo);
                                    return (
                                        <button
                                            key={p.id}
                                            type="button"
                                            onClick={() => addToCart(p)}
                                            className="w-full text-left px-4 py-3 hover:bg-orange-50 dark:hover:bg-orange-900/10 transition-colors border-b border-gray-100 dark:border-gray-800 last:border-0 flex items-center gap-3"
                                        >
                                            <div
                                                className={clsx(
                                                    "flex items-center justify-center w-8 h-8 rounded-lg shrink-0",
                                                    tipoColor(p.tipo)
                                                )}
                                            >
                                                <Icon className="h-4 w-4" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="font-medium text-gray-900 dark:text-gray-100 text-sm truncate">
                                                    {p.nombre}
                                                </div>
                                                <div className="text-xs text-gray-500 dark:text-gray-400">
                                                    {p.codigo} · {p.tipo}
                                                </div>
                                            </div>
                                            <div className="text-right shrink-0">
                                                <div className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                                                    {formatCurrency(
                                                        p.precio_unitario,
                                                        p.moneda
                                                    )}
                                                </div>
                                                <div className="text-xs text-gray-400">
                                                    {p.moneda}
                                                </div>
                                            </div>
                                            <Plus className="h-4 w-4 text-orange-600 shrink-0" />
                                        </button>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                </div>

                {/* Cart items */}
                {cart.length === 0 ? (
                    <div className="p-12 text-center">
                        <ShoppingCart className="h-12 w-12 text-gray-300 dark:text-gray-700 mx-auto mb-3" />
                        <p className="text-gray-500 dark:text-gray-400 font-medium">
                            El carrito está vacío
                        </p>
                        <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
                            Busca y agrega productos arriba
                        </p>
                    </div>
                ) : (
                    <div>
                        {/* Header row */}
                        <div className="grid grid-cols-12 gap-4 px-4 py-2 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide bg-gray-50 dark:bg-gray-800/50">
                            <div className="col-span-5">Producto</div>
                            <div className="col-span-2 text-right">Precio</div>
                            <div className="col-span-2 text-center">
                                Cantidad
                            </div>
                            <div className="col-span-2 text-right">
                                Subtotal
                            </div>
                            <div className="col-span-1"></div>
                        </div>

                        {/* Items */}
                        {cart.map((ci) => {
                            const Icon = tipoIcon(ci.producto.tipo);
                            const itemSubtotal =
                                ci.producto.precio_unitario * ci.cantidad;
                            return (
                                <div
                                    key={ci.producto.id}
                                    className="grid grid-cols-12 gap-4 items-center px-4 py-3 border-b border-gray-100 dark:border-gray-800 last:border-0 hover:bg-gray-50/50 dark:hover:bg-gray-800/20 transition-colors"
                                >
                                    {/* Product info */}
                                    <div className="col-span-5 flex items-center gap-2">
                                        <div
                                            className={clsx(
                                                "flex items-center justify-center w-7 h-7 rounded-lg shrink-0",
                                                tipoColor(ci.producto.tipo)
                                            )}
                                        >
                                            <Icon className="h-3.5 w-3.5" />
                                        </div>
                                        <div className="min-w-0">
                                            <div className="font-medium text-gray-900 dark:text-gray-100 text-sm truncate">
                                                {ci.producto.nombre}
                                            </div>
                                            <div className="text-xs text-gray-400">
                                                {ci.producto.codigo}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Price */}
                                    <div className="col-span-2 text-right text-sm text-gray-700 dark:text-gray-300">
                                        {(ci.producto.moneda || "PEN") !== moneda ? (
                                            <>
                                                <div className="font-semibold">
                                                    {formatCurrency(
                                                        convertPrice(ci.producto.precio_unitario, ci.producto.moneda),
                                                        moneda
                                                    )}
                                                </div>
                                                <div className="flex items-center justify-end gap-1 text-xs text-gray-400 mt-0.5 line-through">
                                                    {formatCurrency(
                                                        ci.producto.precio_unitario,
                                                        ci.producto.moneda
                                                    )}
                                                </div>
                                            </>
                                        ) : (
                                            <div>
                                                {formatCurrency(
                                                    ci.producto.precio_unitario,
                                                    ci.producto.moneda
                                                )}
                                            </div>
                                        )}
                                    </div>

                                    {/* Quantity */}
                                    <div className="col-span-2 flex items-center justify-center gap-1">
                                        <button
                                            type="button"
                                            onClick={() =>
                                                updateQuantity(
                                                    ci.producto.id,
                                                    -1
                                                )
                                            }
                                            className="p-1 rounded-lg text-gray-400 hover:text-orange-600 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-colors"
                                        >
                                            <Minus className="h-3.5 w-3.5" />
                                        </button>
                                        <input
                                            type="number"
                                            min={1}
                                            value={ci.cantidad}
                                            onChange={(e) =>
                                                setQuantity(
                                                    ci.producto.id,
                                                    Number(e.target.value)
                                                )
                                            }
                                            className="w-14 text-center rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 py-1 text-sm outline-none focus:border-orange-500"
                                        />
                                        <button
                                            type="button"
                                            onClick={() =>
                                                updateQuantity(
                                                    ci.producto.id,
                                                    1
                                                )
                                            }
                                            className="p-1 rounded-lg text-gray-400 hover:text-orange-600 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-colors"
                                        >
                                            <Plus className="h-3.5 w-3.5" />
                                        </button>
                                    </div>

                                    {/* Subtotal */}
                                    <div className="col-span-2 text-right font-semibold text-gray-900 dark:text-gray-100 text-sm">
                                        {formatCurrency(
                                            convertPrice(ci.producto.precio_unitario, ci.producto.moneda) * ci.cantidad,
                                            moneda
                                        )}
                                    </div>

                                    {/* Remove */}
                                    <div className="col-span-1 flex justify-end">
                                        <button
                                            type="button"
                                            onClick={() =>
                                                removeFromCart(ci.producto.id)
                                            }
                                            className="p-1.5 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    </div>
                                </div>
                            );
                        })}

                        {/* Totals */}
                        <div className="bg-gray-50 dark:bg-gray-800/50 px-4 py-4 space-y-2">
                            {hasMixedCurrencies && tcVenta && (
                                <div className="flex items-center gap-2 text-xs text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 rounded-lg px-3 py-2 mb-2">
                                    <ArrowRightLeft className="h-3.5 w-3.5 shrink-0" />
                                    <span>T.C. SUNAT del día: <strong>S/ {tipoCambio?.venta}</strong> (venta) · Precios convertidos automáticamente.</span>
                                </div>
                            )}
                            {hasMixedCurrencies && !tcVenta && (
                                <div className="flex items-center gap-2 text-xs text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 rounded-lg px-3 py-2 mb-2">
                                    <ArrowRightLeft className="h-3.5 w-3.5 shrink-0" />
                                    <span>No se pudo obtener el tipo de cambio. Los totales se muestran sin conversión.</span>
                                </div>
                            )}
                            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                                <span>Subtotal</span>
                                <span>{formatCurrency(subtotal, moneda)}</span>
                            </div>
                            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                                <span>IGV</span>
                                <span>{formatCurrency(igvTotal, moneda)}</span>
                            </div>
                            <div className="border-t border-gray-200 dark:border-gray-700 pt-2 flex justify-between text-base font-bold text-gray-900 dark:text-gray-100">
                                <span>Total</span>
                                <span>{formatCurrency(total, moneda)}</span>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* ── Notes ── */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                        Notas Internas
                    </label>
                    <textarea
                        value={notasInternas}
                        onChange={(e) => setNotasInternas(e.target.value)}
                        rows={3}
                        placeholder="Notas visibles solo para tu equipo..."
                        className="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-4 py-2.5 text-sm outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all resize-none"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                        Términos y Condiciones
                    </label>
                    <textarea
                        value={terminosCondiciones}
                        onChange={(e) =>
                            setTerminosCondiciones(e.target.value)
                        }
                        rows={3}
                        placeholder="Términos visibles para el cliente..."
                        className="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-4 py-2.5 text-sm outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all resize-none"
                    />
                </div>
            </div>

            {/* ── Commercial conditions ── */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                        Forma de Pago
                    </label>
                    <select
                        value={formaPago}
                        onChange={(e) => setFormaPago(e.target.value)}
                        className="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2.5 text-sm outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all"
                    >
                        <option value="">Seleccionar...</option>
                        <option className="dark:bg-gray-800" value="contado">Contado</option>
                        <option className="dark:bg-gray-800" value="credito_15">Crédito 15 días</option>
                        <option className="dark:bg-gray-800" value="credito_30">Crédito 30 días</option>
                        <option className="dark:bg-gray-800" value="credito_60">Crédito 60 días</option>
                        <option className="dark:bg-gray-800" value="credito_90">Crédito 90 días</option>
                    </select>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                        Tiempo de Entrega
                    </label>
                    <input
                        type="text"
                        value={tiempoEntrega}
                        onChange={(e) => setTiempoEntrega(e.target.value)}
                        placeholder="Ej: 3 días hábiles"
                        className="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-4 py-2.5 text-sm outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                        Lugar de Entrega
                    </label>
                    <input
                        type="text"
                        value={lugarEntrega}
                        onChange={(e) => setLugarEntrega(e.target.value)}
                        placeholder="Ej: Almacén del cliente"
                        className="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-4 py-2.5 text-sm outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all"
                    />
                </div>
            </div>

            {/* ── Submit ── */}
            <div className="flex justify-end gap-3 pt-2">
                <Link
                    href="/dashboard/cotizaciones"
                    className="rounded-xl border border-gray-200 dark:border-gray-700 px-5 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                    Cancelar
                </Link>
                <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={isSubmitting}
                    className="inline-flex items-center gap-2 rounded-xl bg-orange-600 px-5 py-2.5 text-sm font-medium text-white shadow-lg shadow-orange-500/20 hover:bg-orange-700 hover:shadow-orange-500/30 transition-all disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer"
                >
                    {isSubmitting && (
                        <Loader2 className="h-4 w-4 animate-spin" />
                    )}
                    {isSubmitting
                        ? "Creando..."
                        : "Crear Cotización"}
                </button>
            </div>
        </div>
    );
}
