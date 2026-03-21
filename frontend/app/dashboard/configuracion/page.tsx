"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/hooks/useAuth";
import {
    obtenerPerfil, actualizarPerfil, cambiarPassword,
    obtenerConfigEmpresa, actualizarConfigEmpresa,
    subirLogo, eliminarLogo,
    listarCuentasBancarias, crearCuentaBancaria, actualizarCuentaBancaria, eliminarCuentaBancaria,
    listarUsuarios, crearUsuario, actualizarUsuario, eliminarUsuario,
    obtenerAuditLogs,
} from "@/services/configuracion.service";
import type {
    Perfil, ConfigEmpresa, CuentaBancaria, CuentaBancariaForm,
    UsuarioAdmin, CrearUsuarioForm, AuditLog, AuditLogsResponse,
} from "@/types/configuracion";
import {
    User, Building2, Landmark, Users, ScrollText, Save, Plus, Pencil, Trash2,
    Eye, EyeOff, Loader2, CheckCircle2, XCircle, Shield, ChevronDown,
    Upload, ImageIcon,
} from "lucide-react";

/* ── Roles config ── */
const TABS_BY_ROLE: Record<string, string[]> = {
    admin: ["mi-cuenta", "empresa", "cuentas-bancarias", "usuarios", "auditoria"],
    contador: ["mi-cuenta", "empresa", "cuentas-bancarias", "usuarios", "auditoria"],
    gerente_ventas: ["mi-cuenta", "empresa", "cuentas-bancarias"],
    vendedor: ["mi-cuenta"],
    operario: ["mi-cuenta"],
    readonly: ["mi-cuenta"],
};

const TAB_META: Record<string, { label: string; icon: React.ElementType }> = {
    "mi-cuenta": { label: "Mi Cuenta", icon: User },
    empresa: { label: "Empresa", icon: Building2 },
    "cuentas-bancarias": { label: "Cuentas Bancarias", icon: Landmark },
    usuarios: { label: "Usuarios", icon: Users },
    auditoria: { label: "Auditoría", icon: ScrollText },
};

const ROLES_OPTIONS = [
    { value: "admin", label: "Administrador" },
    { value: "contador", label: "Contador" },
    { value: "gerente_ventas", label: "Gerente de Ventas" },
    { value: "vendedor", label: "Vendedor" },
    { value: "operario", label: "Operario" },
    { value: "readonly", label: "Solo Lectura" },
];

const BANCOS = ["BCP", "BBVA", "Interbank", "Scotiabank", "BanBif", "Banco de la Nación", "Banco Pichincha", "Citibank", "Banco GNB"];

/* ── Toast ── */
function Toast({ msg, type, onClose }: { msg: string; type: "ok" | "err"; onClose: () => void }) {
    useEffect(() => { const t = setTimeout(onClose, 3500); return () => clearTimeout(t); }, [onClose]);
    return (
        <div className={`fixed top-6 right-6 z-[100] flex items-center gap-2 px-5 py-3 rounded-xl shadow-2xl text-sm font-medium animate-in slide-in-from-top-2 ${type === "ok" ? "bg-emerald-600 text-white" : "bg-red-600 text-white"}`}>
            {type === "ok" ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
            {msg}
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════ */
export default function ConfiguracionPage() {
    const { user } = useAuth();
    const rol = user?.rol ?? "readonly";
    const tabs = TABS_BY_ROLE[rol] ?? ["mi-cuenta"];
    const [activeTab, setActiveTab] = useState(tabs[0]);
    const [toast, setToast] = useState<{ msg: string; type: "ok" | "err" } | null>(null);
    const showToast = (msg: string, type: "ok" | "err" = "ok") => setToast({ msg, type });

    return (
        <div className="max-w-6xl mx-auto space-y-6">
            {toast && <Toast msg={toast.msg} type={toast.type} onClose={() => setToast(null)} />}

            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Configuración</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Administra tu cuenta y la configuración de tu empresa</p>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 p-1 bg-gray-100 dark:bg-white/5 rounded-xl overflow-x-auto">
                {tabs.map((t) => {
                    const meta = TAB_META[t];
                    const Icon = meta.icon;
                    return (
                        <button key={t} onClick={() => setActiveTab(t)}
                            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition-all duration-200 ${activeTab === t ? "bg-white dark:bg-white/10 text-[#2E66F6] shadow-sm" : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"}`}
                        >
                            <Icon className="w-4 h-4" />
                            {meta.label}
                        </button>
                    );
                })}
            </div>

            {/* Tab content */}
            <div className="bg-white dark:bg-white/[0.03] border border-gray-200 dark:border-white/10 rounded-2xl shadow-sm">
                {activeTab === "mi-cuenta" && <TabMiCuenta showToast={showToast} isReadonly={rol === "readonly"} />}
                {activeTab === "empresa" && <TabEmpresa showToast={showToast} rol={rol} />}
                {activeTab === "cuentas-bancarias" && <TabCuentasBancarias showToast={showToast} rol={rol} />}
                {activeTab === "usuarios" && <TabUsuarios showToast={showToast} rol={rol} />}
                {activeTab === "auditoria" && <TabAuditoria />}
            </div>
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════
   TAB: MI CUENTA
   ══════════════════════════════════════════════════════════════════════════ */
function TabMiCuenta({ showToast, isReadonly }: { showToast: (m: string, t?: "ok" | "err") => void; isReadonly: boolean }) {
    const [perfil, setPerfil] = useState<Perfil | null>(null);
    const [nombre, setNombre] = useState("");
    const [apellido, setApellido] = useState("");
    const [saving, setSaving] = useState(false);
    const [loading, setLoading] = useState(true);

    // Password
    const [showPwSection, setShowPwSection] = useState(false);
    const [pwActual, setPwActual] = useState("");
    const [pwNuevo, setPwNuevo] = useState("");
    const [showPw, setShowPw] = useState(false);
    const [savingPw, setSavingPw] = useState(false);

    useEffect(() => {
        obtenerPerfil().then((p) => { setPerfil(p); setNombre(p.nombre); setApellido(p.apellido ?? ""); }).catch(() => showToast("Error cargando perfil", "err")).finally(() => setLoading(false));
    }, []);

    const handleSave = async () => {
        setSaving(true);
        try { const p = await actualizarPerfil({ nombre, apellido }); setPerfil(p); showToast("Perfil actualizado"); } catch (e: any) { showToast(e.message, "err"); } finally { setSaving(false); }
    };

    const handlePw = async () => {
        setSavingPw(true);
        try { await cambiarPassword({ password_actual: pwActual, password_nuevo: pwNuevo }); showToast("Contraseña cambiada"); setPwActual(""); setPwNuevo(""); setShowPwSection(false); } catch (e: any) { showToast(e.message, "err"); } finally { setSavingPw(false); }
    };

    if (loading) return <div className="p-12 flex justify-center"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>;

    return (
        <div className="p-6 space-y-8">
            <div className="flex items-center gap-4 pb-6 border-b border-gray-100 dark:border-white/5">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#2E66F6] to-[#1a4fd4] flex items-center justify-center text-white text-xl font-bold shadow-lg shadow-blue-500/20">
                    {perfil?.nombre?.[0]?.toUpperCase()}{perfil?.apellido?.[0]?.toUpperCase() ?? ""}
                </div>
                <div>
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{perfil?.nombre} {perfil?.apellido}</h2>
                    <p className="text-sm text-gray-500">{perfil?.email}</p>
                    <span className="inline-block mt-1 px-2.5 py-0.5 text-xs font-semibold rounded-full bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 capitalize">{perfil?.rol?.replace("_", " ")}</span>
                </div>
            </div>

            {/* Profile form */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Nombre</label>
                    <input value={nombre} onChange={(e) => setNombre(e.target.value)} disabled={isReadonly}
                        className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-white/5 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 outline-none transition disabled:opacity-50" />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Apellido</label>
                    <input value={apellido} onChange={(e) => setApellido(e.target.value)} disabled={isReadonly}
                        className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-white/5 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 outline-none transition disabled:opacity-50" />
                </div>
            </div>

            {!isReadonly && (
                <button onClick={handleSave} disabled={saving}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#2E66F6] hover:bg-[#2559d4] text-white text-sm font-medium transition disabled:opacity-50">
                    {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />} Guardar cambios
                </button>
            )}

            {/* Change password */}
            {!isReadonly && (
                <div className="pt-6 border-t border-gray-100 dark:border-white/5">
                    <button onClick={() => setShowPwSection(!showPwSection)} className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-[#2E66F6] transition">
                        <Shield className="w-4 h-4" /> Cambiar contraseña
                        <ChevronDown className={`w-4 h-4 transition-transform ${showPwSection ? "rotate-180" : ""}`} />
                    </button>
                    {showPwSection && (
                        <div className="mt-4 space-y-4">
                            <div className="relative">
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Contraseña actual</label>
                                <input type={showPw ? "text" : "password"} value={pwActual} onChange={(e) => setPwActual(e.target.value)}
                                    className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-white/5 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 outline-none transition" />
                                <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-9 text-gray-400">{showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}</button>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Nueva contraseña</label>
                                <input type={showPw ? "text" : "password"} value={pwNuevo} onChange={(e) => setPwNuevo(e.target.value)}
                                    className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-white/5 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 outline-none transition" />
                                <p className="text-xs text-gray-400 mt-1">Mínimo 8 caracteres, 1 mayúscula, 1 número</p>
                            </div>
                            <button onClick={handlePw} disabled={savingPw || !pwActual || !pwNuevo}
                                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-sm font-medium transition disabled:opacity-50">
                                {savingPw ? <Loader2 className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />} Cambiar contraseña
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════
   TAB: EMPRESA
   ══════════════════════════════════════════════════════════════════════════ */
function TabEmpresa({ showToast, rol }: { showToast: (m: string, t?: "ok" | "err") => void; rol: string }) {
    const [config, setConfig] = useState<ConfigEmpresa | null>(null);
    const [form, setForm] = useState({ serie_factura: "", serie_boleta: "", serie_nc: "", serie_nd: "", logo_url: "", telefono: "", email: "" });
    const [saving, setSaving] = useState(false);
    const [loading, setLoading] = useState(true);
    const canEditSeries = rol === "administrador" || rol === "admin" || rol === "contador";

    // Logo state
    const [logoUrl, setLogoUrl] = useState<string | null>(null);
    const [uploadingLogo, setUploadingLogo] = useState(false);
    const [dragOver, setDragOver] = useState(false);

    useEffect(() => {
        obtenerConfigEmpresa().then((c) => {
            setConfig(c);
            setForm({ serie_factura: c.serie_factura ?? "", serie_boleta: c.serie_boleta ?? "", serie_nc: c.serie_nc ?? "", serie_nd: c.serie_nd ?? "", logo_url: c.logo_url ?? "", telefono: c.telefono ?? "", email: c.email ?? "" });
            setLogoUrl(c.logo_url ?? null);
        }).catch(() => showToast("Error cargando configuración", "err")).finally(() => setLoading(false));
    }, []);

    const handleSave = async () => {
        setSaving(true);
        try {
            const data = canEditSeries ? form : { logo_url: form.logo_url, telefono: form.telefono, email: form.email };
            const c = await actualizarConfigEmpresa(data);
            setConfig(c); showToast("Configuración actualizada");
        } catch (e: any) { showToast(e.message, "err"); } finally { setSaving(false); }
    };

    // ── Logo handlers ──
    const ALLOWED_TYPES = ["image/png", "image/jpeg", "image/jpg"];
    const MAX_SIZE = 2 * 1024 * 1024; // 2 MB

    const validateAndUpload = async (file: File) => {
        if (!ALLOWED_TYPES.includes(file.type)) {
            showToast("Solo se permiten archivos PNG o JPEG", "err");
            return;
        }
        if (file.size > MAX_SIZE) {
            showToast("El archivo excede 2 MB", "err");
            return;
        }
        setUploadingLogo(true);
        try {
            const res = await subirLogo(file);
            setLogoUrl(res.logo_url);
            showToast("Logo actualizado correctamente");
        } catch (e: any) {
            showToast(e.message || "Error subiendo logo", "err");
        } finally {
            setUploadingLogo(false);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) validateAndUpload(file);
        e.target.value = "";
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setDragOver(false);
        const file = e.dataTransfer.files?.[0];
        if (file) validateAndUpload(file);
    };

    const handleDeleteLogo = async () => {
        if (!confirm("¿Eliminar el logo de la empresa?")) return;
        try {
            await eliminarLogo();
            setLogoUrl(null);
            showToast("Logo eliminado");
        } catch (e: any) {
            showToast(e.message || "Error eliminando logo", "err");
        }
    };

    if (loading) return <div className="p-12 flex justify-center"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>;

    const inputCls = "w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-white/5 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 outline-none transition disabled:opacity-50";

    return (
        <div className="p-6 space-y-8">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2"><Building2 className="w-5 h-5 text-[#FF7043]" /> Datos de Empresa</h2>

            {/* ── Logo Section ── */}
            <div className="space-y-3">
                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Logo de la empresa</h3>
                <p className="text-xs text-gray-400 dark:text-gray-500">Este logo aparecerá en la esquina superior izquierda de tus cotizaciones y facturas en PDF.</p>

                <div className="flex items-start gap-6">
                    {/* Preview */}
                    <div className="shrink-0 w-[200px] h-[80px] rounded-xl border-2 border-dashed border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-white/5 flex items-center justify-center overflow-hidden">
                        {logoUrl ? (
                            <img src={logoUrl} alt="Logo empresa" className="max-w-full max-h-full object-contain" />
                        ) : (
                            <ImageIcon className="w-8 h-8 text-gray-300 dark:text-gray-600" />
                        )}
                    </div>

                    {/* Upload zone */}
                    <div className="flex-1 space-y-3">
                        <label
                            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                            onDragLeave={() => setDragOver(false)}
                            onDrop={handleDrop}
                            className={`relative flex flex-col items-center justify-center gap-2 px-6 py-5 rounded-xl border-2 border-dashed cursor-pointer transition-all duration-200 ${dragOver
                                ? "border-[#2E66F6] bg-blue-50/50 dark:bg-blue-900/10"
                                : "border-gray-200 dark:border-white/10 hover:border-[#2E66F6]/50 hover:bg-gray-50/50 dark:hover:bg-white/[0.02]"
                                }`}
                        >
                            <input type="file" accept=".png,.jpg,.jpeg" onChange={handleFileChange} className="sr-only" />
                            {uploadingLogo ? (
                                <Loader2 className="w-6 h-6 animate-spin text-[#2E66F6]" />
                            ) : (
                                <Upload className="w-6 h-6 text-gray-400" />
                            )}
                            <div className="text-center">
                                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                    {uploadingLogo ? "Subiendo..." : "Arrastra tu logo aquí o haz clic para seleccionar"}
                                </p>
                                <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                                    PNG o JPEG · Máx 2 MB · Recomendado: 400×150 px
                                </p>
                            </div>
                        </label>

                        {logoUrl && (
                            <button onClick={handleDeleteLogo}
                                className="flex items-center gap-1.5 text-xs font-medium text-red-500 hover:text-red-600 transition">
                                <Trash2 className="w-3.5 h-3.5" /> Eliminar logo
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* Contact info */}
            <div className="space-y-2">
                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Información de contacto</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Teléfono</label>
                        <input value={form.telefono} onChange={(e) => setForm({ ...form, telefono: e.target.value })} className={inputCls} placeholder="01-234-5678" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Email</label>
                        <input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className={inputCls} placeholder="ventas@empresa.com" />
                    </div>
                </div>
            </div>

            <button onClick={handleSave} disabled={saving}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#2E66F6] hover:bg-[#2559d4] text-white text-sm font-medium transition disabled:opacity-50">
                {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />} Guardar cambios
            </button>
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════
   TAB: CUENTAS BANCARIAS
   ══════════════════════════════════════════════════════════════════════════ */
function TabCuentasBancarias({ showToast, rol }: { showToast: (m: string, t?: "ok" | "err") => void; rol: string }) {
    const [cuentas, setCuentas] = useState<CuentaBancaria[]>([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editId, setEditId] = useState<number | null>(null);
    const [saving, setSaving] = useState(false);
    const emptyForm: CuentaBancariaForm = { nombre_banco: "BCP", numero_cuenta: "", cci: "", moneda: "PEN", tipo_cuenta: "corriente", titular: "" };
    const [form, setForm] = useState<CuentaBancariaForm>(emptyForm);

    const canCreate = ["administrador", "admin", "contador", "gerente_ventas"].includes(rol);
    const canEdit = ["administrador", "admin", "contador"].includes(rol);
    const canDelete = rol === "administrador" || rol === "admin";

    const load = useCallback(() => {
        setLoading(true);
        listarCuentasBancarias().then(setCuentas).catch(() => showToast("Error cargando cuentas", "err")).finally(() => setLoading(false));
    }, []);

    useEffect(() => { load(); }, [load]);

    const openCreate = () => { setEditId(null); setForm(emptyForm); setShowForm(true); };
    const openEdit = (c: CuentaBancaria) => { setEditId(c.id); setForm({ nombre_banco: c.nombre_banco, numero_cuenta: c.numero_cuenta, cci: c.cci ?? "", moneda: c.moneda, tipo_cuenta: c.tipo_cuenta, titular: c.titular }); setShowForm(true); };

    const handleSave = async () => {
        setSaving(true);
        try {
            if (editId) { await actualizarCuentaBancaria(editId, form); showToast("Cuenta actualizada"); }
            else { await crearCuentaBancaria(form); showToast("Cuenta creada"); }
            setShowForm(false); load();
        } catch (e: any) { showToast(e.message, "err"); } finally { setSaving(false); }
    };

    const handleDelete = async (id: number) => {
        if (!confirm("¿Eliminar esta cuenta bancaria?")) return;
        try { await eliminarCuentaBancaria(id); showToast("Cuenta eliminada"); load(); } catch (e: any) { showToast(e.message, "err"); }
    };

    const inputCls = "w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-white/5 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 outline-none transition";
    const selectCls = inputCls + " appearance-none";

    if (loading) return <div className="p-12 flex justify-center"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>;

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2"><Landmark className="w-5 h-5 text-[#FF7043]" /> Cuentas Bancarias</h2>
                {canCreate && !showForm && (
                    <button onClick={openCreate} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#2E66F6] hover:bg-[#2559d4] text-white text-sm font-medium transition">
                        <Plus className="w-4 h-4" /> Nueva cuenta
                    </button>
                )}
            </div>

            {/* Form */}
            {showForm && (
                <div className="p-5 bg-gray-50 dark:bg-white/5 rounded-xl border border-gray-200 dark:border-white/10 space-y-4">
                    <h3 className="font-medium text-gray-900 dark:text-white">{editId ? "Editar" : "Nueva"} Cuenta Bancaria</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Banco</label>
                            <select value={form.nombre_banco} onChange={(e) => setForm({ ...form, nombre_banco: e.target.value })} className={selectCls}>
                                {BANCOS.map((b) => <option className="dark:bg-gray-800" key={b} value={b}>{b}</option>)}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Número de cuenta</label>
                            <input value={form.numero_cuenta} onChange={(e) => setForm({ ...form, numero_cuenta: e.target.value })} className={inputCls} />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">CCI <span className="text-gray-400">(opcional)</span></label>
                            <input value={form.cci} onChange={(e) => setForm({ ...form, cci: e.target.value })} className={inputCls} maxLength={20} />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Moneda</label>
                            <select value={form.moneda} onChange={(e) => setForm({ ...form, moneda: e.target.value })} className={selectCls}>
                                <option className="dark:bg-gray-800" value="PEN">Soles (PEN)</option>
                                <option className="dark:bg-gray-800" value="USD">Dólares (USD)</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Tipo de cuenta</label>
                            <select value={form.tipo_cuenta} onChange={(e) => setForm({ ...form, tipo_cuenta: e.target.value })} className={selectCls}>
                                <option className="dark:bg-gray-800" value="corriente">Corriente</option>
                                <option className="dark:bg-gray-800" value="ahorros">Ahorros</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Titular</label>
                            <input value={form.titular} onChange={(e) => setForm({ ...form, titular: e.target.value })} className={inputCls} />
                        </div>
                    </div>
                    <div className="flex gap-3">
                        <button onClick={handleSave} disabled={saving || !form.numero_cuenta || !form.titular}
                            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#2E66F6] hover:bg-[#2559d4] text-white text-sm font-medium transition disabled:opacity-50">
                            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />} {editId ? "Actualizar" : "Crear"}
                        </button>
                        <button onClick={() => setShowForm(false)} className="px-5 py-2.5 rounded-xl border border-gray-200 dark:border-white/10 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/5 transition">Cancelar</button>
                    </div>
                </div>
            )}

            {/* Table */}
            {cuentas.length === 0 ? (
                <div className="text-center py-16 text-gray-400">
                    <Landmark className="w-12 h-12 mx-auto mb-3 opacity-30" />
                    <p className="font-medium">No hay cuentas bancarias</p>
                    <p className="text-sm mt-1">Agrega tu primera cuenta para mostrarla en cotizaciones</p>
                </div>
            ) : (
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-gray-100 dark:border-white/5">
                                <th className="text-left py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">Banco</th>
                                <th className="text-left py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">N° Cuenta</th>
                                <th className="text-left py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">CCI</th>
                                <th className="text-left py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">Moneda</th>
                                <th className="text-left py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">Tipo</th>
                                <th className="text-left py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">Titular</th>
                                {(canEdit || canDelete) && <th className="text-right py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">Acciones</th>}
                            </tr>
                        </thead>
                        <tbody>
                            {cuentas.map((c) => (
                                <tr key={c.id} className="border-b border-gray-50 dark:border-white/5 hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition">
                                    <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">{c.nombre_banco}</td>
                                    <td className="py-3 px-4 text-gray-600 dark:text-gray-300 font-mono text-xs">{c.numero_cuenta}</td>
                                    <td className="py-3 px-4 text-gray-500 font-mono text-xs">{c.cci || "—"}</td>
                                    <td className="py-3 px-4">
                                        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${c.moneda === "PEN" ? "bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"}`}>{c.moneda}</span>
                                    </td>
                                    <td className="py-3 px-4 text-gray-600 dark:text-gray-300 capitalize">{c.tipo_cuenta}</td>
                                    <td className="py-3 px-4 text-gray-600 dark:text-gray-300">{c.titular}</td>
                                    {(canEdit || canDelete) && (
                                        <td className="py-3 px-4 text-right">
                                            <div className="flex justify-end gap-1">
                                                {canEdit && <button onClick={() => openEdit(c)} className="p-1.5 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 text-gray-400 hover:text-blue-600 transition"><Pencil className="w-4 h-4" /></button>}
                                                {canDelete && <button onClick={() => handleDelete(c.id)} className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-400 hover:text-red-600 transition"><Trash2 className="w-4 h-4" /></button>}
                                            </div>
                                        </td>
                                    )}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════
   TAB: USUARIOS
   ══════════════════════════════════════════════════════════════════════════ */
function TabUsuarios({ showToast, rol }: { showToast: (m: string, t?: "ok" | "err") => void; rol: string }) {
    const [usuarios, setUsuarios] = useState<UsuarioAdmin[]>([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editId, setEditId] = useState<number | null>(null);
    const [saving, setSaving] = useState(false);
    const [form, setForm] = useState<CrearUsuarioForm>({ email: "", nombre: "", apellido: "", password: "", rol: "vendedor" });
    const [editForm, setEditForm] = useState({ nombre: "", apellido: "", rol: "", estado: "" });

    const canDelete = rol === "administrador" || rol === "admin";

    const load = useCallback(() => {
        setLoading(true);
        listarUsuarios().then(setUsuarios).catch(() => showToast("Error cargando usuarios", "err")).finally(() => setLoading(false));
    }, []);

    useEffect(() => { load(); }, [load]);

    const handleCreate = async () => {
        setSaving(true);
        try { await crearUsuario(form); showToast("Usuario creado"); setShowForm(false); setForm({ email: "", nombre: "", apellido: "", password: "", rol: "vendedor" }); load(); }
        catch (e: any) { showToast(e.message, "err"); } finally { setSaving(false); }
    };

    const openEdit = (u: UsuarioAdmin) => { setEditId(u.id); setEditForm({ nombre: u.nombre, apellido: u.apellido ?? "", rol: u.rol, estado: u.estado }); };

    const handleUpdate = async () => {
        if (!editId) return;
        setSaving(true);
        try { await actualizarUsuario(editId, editForm); showToast("Usuario actualizado"); setEditId(null); load(); }
        catch (e: any) { showToast(e.message, "err"); } finally { setSaving(false); }
    };

    const handleDelete = async (id: number) => {
        if (!confirm("¿Eliminar este usuario?")) return;
        try { await eliminarUsuario(id); showToast("Usuario eliminado"); load(); } catch (e: any) { showToast(e.message, "err"); }
    };

    const inputCls = "w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-white/5 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 outline-none transition";
    const selectCls = inputCls + " appearance-none";

    const estadoBadge = (e: string) => {
        const map: Record<string, string> = { activo: "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400", inactivo: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400", bloqueado: "bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400" };
        return map[e] ?? map.activo;
    };

    if (loading) return <div className="p-12 flex justify-center"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>;

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2"><Users className="w-5 h-5 text-[#FF7043]" /> Usuarios</h2>
                {!showForm && <button onClick={() => { setShowForm(true); setEditId(null); }} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#2E66F6] hover:bg-[#2559d4] text-white text-sm font-medium transition"><Plus className="w-4 h-4" /> Nuevo usuario</button>}
            </div>

            {/* Create form */}
            {showForm && (
                <div className="p-5 bg-gray-50 dark:bg-white/5 rounded-xl border border-gray-200 dark:border-white/10 space-y-4">
                    <h3 className="font-medium text-gray-900 dark:text-white">Nuevo Usuario</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Email</label><input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className={inputCls} type="email" /></div>
                        <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Nombre</label><input value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} className={inputCls} /></div>
                        <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Apellido</label><input value={form.apellido} onChange={(e) => setForm({ ...form, apellido: e.target.value })} className={inputCls} /></div>
                        <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Contraseña</label><input value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className={inputCls} type="password" /></div>
                        <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Rol</label>
                            <select value={form.rol} onChange={(e) => setForm({ ...form, rol: e.target.value })} className={selectCls}>
                                {ROLES_OPTIONS.map((r) => <option className="dark:bg-gray-800" key={r.value} value={r.value}>{r.label}</option>)}
                            </select>
                        </div>
                    </div>
                    <div className="flex gap-3">
                        <button onClick={handleCreate} disabled={saving || !form.email || !form.nombre || !form.password} className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#2E66F6] hover:bg-[#2559d4] text-white text-sm font-medium transition disabled:opacity-50">{saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />} Crear usuario</button>
                        <button onClick={() => setShowForm(false)} className="px-5 py-2.5 rounded-xl border border-gray-200 dark:border-white/10 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/5 transition">Cancelar</button>
                    </div>
                </div>
            )}

            {/* Users table */}
            <div className="overflow-x-auto">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-gray-100 dark:border-white/5">
                            <th className="text-left py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">Nombre</th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">Email</th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">Rol</th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">Estado</th>
                            <th className="text-right py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {usuarios.map((u) => (
                            <tr key={u.id} className="border-b border-gray-50 dark:border-white/5 hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition">
                                {editId === u.id ? (
                                    <>
                                        <td className="py-2 px-4"><input value={editForm.nombre} onChange={(e) => setEditForm({ ...editForm, nombre: e.target.value })} className={inputCls + " !py-1.5"} /></td>
                                        <td className="py-2 px-4 text-gray-500">{u.email}</td>
                                        <td className="py-2 px-4">
                                            <select value={editForm.rol} onChange={(e) => setEditForm({ ...editForm, rol: e.target.value })} className={selectCls + " !py-1.5"}>
                                                {ROLES_OPTIONS.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
                                            </select>
                                        </td>
                                        <td className="py-2 px-4">
                                            <select value={editForm.estado} onChange={(e) => setEditForm({ ...editForm, estado: e.target.value })} className={selectCls + " !py-1.5"}>
                                                <option value="activo">Activo</option><option value="inactivo">Inactivo</option><option value="bloqueado">Bloqueado</option>
                                            </select>
                                        </td>
                                        <td className="py-2 px-4 text-right">
                                            <div className="flex justify-end gap-1">
                                                <button onClick={handleUpdate} disabled={saving} className="px-3 py-1.5 rounded-lg bg-emerald-600 text-white text-xs font-medium hover:bg-emerald-700 transition disabled:opacity-50">{saving ? "..." : "Guardar"}</button>
                                                <button onClick={() => setEditId(null)} className="px-3 py-1.5 rounded-lg border border-gray-200 dark:border-white/10 text-xs font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/5 transition">Cancelar</button>
                                            </div>
                                        </td>
                                    </>
                                ) : (
                                    <>
                                        <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">{u.nombre} {u.apellido}</td>
                                        <td className="py-3 px-4 text-gray-500">{u.email}</td>
                                        <td className="py-3 px-4"><span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400 capitalize">{u.rol.replace("_", " ")}</span></td>
                                        <td className="py-3 px-4"><span className={`px-2 py-0.5 rounded-full text-xs font-semibold capitalize ${estadoBadge(u.estado)}`}>{u.estado}</span></td>
                                        <td className="py-3 px-4 text-right">
                                            <div className="flex justify-end gap-1">
                                                <button onClick={() => openEdit(u)} className="p-1.5 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 text-gray-400 hover:text-blue-600 transition"><Pencil className="w-4 h-4" /></button>
                                                {canDelete && u.rol !== "administrador" && u.rol !== "admin" && <button onClick={() => handleDelete(u.id)} className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-400 hover:text-red-600 transition"><Trash2 className="w-4 h-4" /></button>}
                                            </div>
                                        </td>
                                    </>
                                )}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════
   TAB: AUDITORÍA
   ══════════════════════════════════════════════════════════════════════════ */
function TabAuditoria() {
    const [logs, setLogs] = useState<AuditLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [total, setTotal] = useState(0);

    const load = useCallback(() => {
        setLoading(true);
        obtenerAuditLogs(page, 20)
            .then((res) => { setLogs(res.items); setTotalPages(res.total_pages); setTotal(res.total); })
            .catch(() => { })
            .finally(() => setLoading(false));
    }, [page]);

    useEffect(() => { load(); }, [load]);

    if (loading) return <div className="p-12 flex justify-center"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>;

    const accionBadge = (a: string) => {
        if (a.startsWith("crear")) return "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400";
        if (a.startsWith("actualizar") || a.startsWith("editar")) return "bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400";
        if (a.startsWith("eliminar")) return "bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400";
        return "bg-gray-100 text-gray-700 dark:bg-white/10 dark:text-gray-300";
    };

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2"><ScrollText className="w-5 h-5 text-[#FF7043]" /> Auditoría</h2>
                {total > 0 && <span className="text-xs text-gray-400">{total} registros</span>}
            </div>

            {logs.length === 0 ? (
                <div className="text-center py-16 text-gray-400">
                    <ScrollText className="w-12 h-12 mx-auto mb-3 opacity-30" />
                    <p className="font-medium">No hay registros de auditoría</p>
                    <p className="text-sm mt-1">Las acciones importantes se registrarán aquí</p>
                </div>
            ) : (
                <>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-gray-100 dark:border-white/5">
                                    <th className="text-left py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">Fecha</th>
                                    <th className="text-left py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">Usuario</th>
                                    <th className="text-left py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">Acción</th>
                                    <th className="text-left py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">Tabla</th>
                                    <th className="text-left py-3 px-4 font-semibold text-gray-500 dark:text-gray-400">Descripción</th>
                                </tr>
                            </thead>
                            <tbody>
                                {logs.map((log) => (
                                    <tr key={log.id} className="border-b border-gray-50 dark:border-white/5 hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition">
                                        <td className="py-3 px-4 text-gray-500 text-xs whitespace-nowrap">{log.created_at ? new Date(log.created_at).toLocaleString("es-PE") : "—"}</td>
                                        <td className="py-3 px-4 text-gray-700 dark:text-gray-300 text-sm">{log.usuario_nombre}</td>
                                        <td className="py-3 px-4"><span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${accionBadge(log.accion)}`}>{log.accion.replace(/_/g, " ")}</span></td>
                                        <td className="py-3 px-4 text-gray-600 dark:text-gray-300 font-mono text-xs">{log.tabla}</td>
                                        <td className="py-3 px-4 text-gray-500 max-w-xs truncate">{log.descripcion || "—"}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    <div className="flex items-center justify-center gap-2">
                        <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="px-4 py-2 rounded-lg border border-gray-200 dark:border-white/10 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-white/5 transition disabled:opacity-30">Anterior</button>
                        <span className="px-4 py-2 text-sm text-gray-500">Página {page} de {totalPages}</span>
                        <button onClick={() => setPage(page + 1)} disabled={page >= totalPages} className="px-4 py-2 rounded-lg border border-gray-200 dark:border-white/10 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-white/5 transition disabled:opacity-30">Siguiente</button>
                    </div>
                </>
            )}
        </div>
    );
}
