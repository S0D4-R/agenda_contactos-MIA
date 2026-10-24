"""
ui/app.py
=========
Ventana principal de la aplicación — menú y dashboard cyberpunk.
"""

import tkinter as tk
from tkinter import messagebox
from pathlib import Path

from core.archivo_manager import ArchivoManager
from ui import theme
from ui.widgets import CyberpunkButton, StatusBar


class App(tk.Tk):
    """
    Raíz de la aplicación. Muestra el dashboard principal con
    el menú de navegación y las estadísticas del sistema.
    """

    def __init__(self) -> None:
        super().__init__()
        self.manager = ArchivoManager()

        # Verificar integridad al iniciar
        self._check_integrity_on_start()

        self.title("◈ AGENDA DE CONTACTOS — ACCESO ALEATORIO ◈")
        self.configure(bg=theme.BG_DEEP)
        self.geometry("900x580")
        self.minsize(750, 460)
        self.resizable(True, True)

        self._build_ui()
        self._update_stats()

    # ── Integridad al inicio ──────────────────────────────────────────────────

    def _check_integrity_on_start(self) -> None:
        self.manager.inicializar_hash_si_falta()
        ok, _, _ = self.manager.verificar_integridad()
        if not ok:
            messagebox.showwarning(
                "⚠  Advertencia de integridad",
                "El archivo de contactos fue modificado fuera de la aplicación.\n"
                "Verifica la integridad desde el menú Herramientas.",
            )

    # ── Construcción de UI ────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self._build_header()
        self._build_body()
        self._build_footer()

    # ── Cabecera ──────────────────────────────────────────────────────────────

    def _build_header(self) -> None:
        hdr = tk.Frame(self, bg=theme.BG_DEEP)
        hdr.pack(fill="x", padx=0, pady=0)

        # Banda superior neón
        tk.Frame(hdr, bg=theme.NEON_CYAN, height=3).pack(fill="x")

        inner = tk.Frame(hdr, bg=theme.BG_DEEP, pady=theme.PAD_LG)
        inner.pack(fill="x", padx=theme.PAD_LG)

        # Título glitch
        title_col = tk.Frame(inner, bg=theme.BG_DEEP)
        title_col.pack(side="left")

        tk.Label(
            title_col,
            text="AGENDA",
            font=("Courier", 32, "bold"),
            fg=theme.NEON_CYAN,
            bg=theme.BG_DEEP,
        ).pack(anchor="w")

        tk.Label(
            title_col,
            text="DE  CONTACTOS  //  ACCESO  ALEATORIO",
            font=("Courier", 10),
            fg=theme.NEON_MAGENTA,
            bg=theme.BG_DEEP,
        ).pack(anchor="w")

        # Stats rápidas (lado derecho del header)
        stats_col = tk.Frame(inner, bg=theme.BG_DEEP)
        stats_col.pack(side="right")

        self._stat_registros = self._stat_block(
            stats_col, "REGISTROS", "0"
        )
        self._stat_archivo = self._stat_block(
            stats_col, "ARCHIVO", "—"
        )
        self._stat_integridad = self._stat_block(
            stats_col, "INTEGRIDAD", "—"
        )

        # Línea separadora
        tk.Frame(self, bg=theme.NEON_MAGENTA, height=1).pack(fill="x")

    def _stat_block(self, parent, label: str, value: str) -> tk.Label:
        """Crea un bloque de estadística y devuelve el Label del valor."""
        frame = tk.Frame(parent, bg=theme.BG_CARD,
                         padx=theme.PAD_MD, pady=theme.PAD_XS)
        frame.pack(side="left", padx=theme.PAD_XS)

        tk.Label(
            frame, text=label,
            font=theme.FONT_MONO_SM,
            fg=theme.TEXT_DIM,
            bg=theme.BG_CARD,
        ).pack()

        val_lbl = tk.Label(
            frame, text=value,
            font=theme.FONT_MONO_LG,
            fg=theme.NEON_CYAN,
            bg=theme.BG_CARD,
        )
        val_lbl.pack()
        return val_lbl

    # ── Cuerpo ────────────────────────────────────────────────────────────────

    def _build_body(self) -> None:
        body = tk.Frame(self, bg=theme.BG_DEEP)
        body.pack(fill="both", expand=True, padx=theme.PAD_LG,
                  pady=theme.PAD_MD)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        self._build_nav(body)
        self._build_dashboard(body)

    def _build_nav(self, parent) -> None:
        nav = tk.Frame(parent, bg=theme.BG_PANEL)
        nav.grid(row=0, column=0, sticky="nsew", padx=(0, theme.PAD_MD))

        # Título de sección
        tk.Frame(nav, bg=theme.NEON_CYAN, height=2).pack(fill="x")
        tk.Label(
            nav, text="  MENÚ PRINCIPAL",
            font=theme.FONT_MONO_MD,
            fg=theme.NEON_CYAN,
            bg=theme.BG_PANEL,
            anchor="w",
            pady=theme.PAD_SM,
        ).pack(fill="x")
        tk.Frame(nav, bg=theme.BORDER, height=1).pack(fill="x")

        menu_items = [
            ("◈  CONTACTOS",    self._open_contactos,   "primary"),
            ("⬡  EXPORTAR",     self._open_exportar,    "primary"),
            ("⚙  HERRAMIENTAS", self._open_herramientas,"primary"),
            ("ℹ  AYUDA",        self._open_ayuda,       "ghost"),
            ("✕  SALIR",        self._salir,            "danger"),
        ]

        for label, cmd, variant in menu_items:
            btn = CyberpunkButton(nav, label, command=cmd, variant=variant)
            btn.configure(anchor="w", width=22)
            btn.pack(fill="x", padx=theme.PAD_SM, pady=theme.PAD_XS)

        # Sello versión
        tk.Label(
            nav, text="\n  v1.0.0  //  2026\n  URL Quetzaltenango",
            font=("Courier", 7),
            fg=theme.TEXT_DIM,
            bg=theme.BG_PANEL,
            anchor="w",
            justify="left",
        ).pack(fill="x", side="bottom", padx=theme.PAD_SM, pady=theme.PAD_SM)

    def _build_dashboard(self, parent) -> None:
        dash = tk.Frame(parent, bg=theme.BG_PANEL)
        dash.grid(row=0, column=1, sticky="nsew")

        tk.Frame(dash, bg=theme.NEON_MAGENTA, height=2).pack(fill="x")
        tk.Label(
            dash, text="  DASHBOARD DEL SISTEMA",
            font=theme.FONT_MONO_MD,
            fg=theme.NEON_MAGENTA,
            bg=theme.BG_PANEL,
            anchor="w",
            pady=theme.PAD_SM,
        ).pack(fill="x")
        tk.Frame(dash, bg=theme.BORDER, height=1).pack(fill="x")

        # Grid de tarjetas info
        cards = tk.Frame(dash, bg=theme.BG_PANEL)
        cards.pack(fill="both", expand=True, padx=theme.PAD_MD,
                   pady=theme.PAD_MD)
        cards.columnconfigure(0, weight=1)
        cards.columnconfigure(1, weight=1)

        self._card_dat   = self._info_card(cards, "ARCHIVO DE DATOS",  0, 0)
        self._card_index = self._info_card(cards, "ÍNDICE PRIMARIO",   0, 1)
        self._card_hash  = self._info_card(cards, "HASH SHA-256",       1, 0)
        self._card_sys   = self._info_card(cards, "ESTRUCTURA",         1, 1)

        # Accesos rápidos
        quick = tk.Frame(dash, bg=theme.BG_PANEL)
        quick.pack(fill="x", padx=theme.PAD_MD, pady=(0, theme.PAD_MD))

        tk.Label(
            quick, text="  ACCESOS RÁPIDOS",
            font=theme.FONT_LABEL,
            fg=theme.TEXT_DIM,
            bg=theme.BG_PANEL,
            anchor="w",
        ).pack(fill="x")

        q_row = tk.Frame(quick, bg=theme.BG_PANEL)
        q_row.pack(fill="x", pady=theme.PAD_XS)

        shortcuts = [
            ("+ Agregar",   self._open_contactos),
            ("⌕ Buscar",    self._open_contactos),
            ("↺ Respaldar", self._open_herramientas),
            ("⬡ Exportar",  self._open_exportar),
        ]
        for label, cmd in shortcuts:
            CyberpunkButton(
                q_row, label, command=cmd, variant="ghost"
            ).pack(side="left", padx=(0, theme.PAD_XS))

    def _info_card(self, parent, title: str, row: int, col: int) -> tk.Label:
        """Crea una tarjeta de info y devuelve el Label de contenido."""
        card = tk.Frame(
            parent, bg=theme.BG_CARD,
            padx=theme.PAD_SM, pady=theme.PAD_SM,
        )
        card.grid(row=row, column=col, sticky="nsew",
                  padx=theme.PAD_XS, pady=theme.PAD_XS)

        tk.Label(
            card, text=title,
            font=theme.FONT_LABEL,
            fg=theme.TEXT_DIM,
            bg=theme.BG_CARD,
            anchor="w",
        ).pack(fill="x")

        tk.Frame(card, bg=theme.BORDER, height=1).pack(fill="x",
                                                        pady=(0, theme.PAD_XS))

        content = tk.Label(
            card, text="cargando...",
            font=theme.FONT_MONO_SM,
            fg=theme.TEXT_MAIN,
            bg=theme.BG_CARD,
            anchor="w",
            justify="left",
        )
        content.pack(fill="x")
        return content

    # ── Footer ────────────────────────────────────────────────────────────────

    def _build_footer(self) -> None:
        tk.Frame(self, bg=theme.BORDER, height=1).pack(fill="x")
        self.status = StatusBar(self)
        self.status.pack(fill="x", side="bottom")

    # ── Actualización de estadísticas ─────────────────────────────────────────

    def _update_stats(self) -> None:
        """Refresca todas las estadísticas del dashboard."""
        info = self.manager.info_archivo()
        idx  = self.manager.get_index()
        ok, guardado, actual = self.manager.verificar_integridad()

        total = info.get("registros", 0)
        size  = info.get("tamaño_bytes", 0)
        ts    = info.get("ultima_modificacion", "—")

        # Header stats
        self._stat_registros.configure(text=str(total))
        self._stat_archivo.configure(
            text=f"{size / 1024:.1f} KB" if size else "0 KB"
        )
        self._stat_integridad.configure(
            text="OK" if ok else "⚠",
            fg=theme.SUCCESS if ok else theme.DANGER,
        )

        # Cards
        self._card_dat.configure(
            text=(
                f"ruta   : {info.get('ruta', '—')}\n"
                f"tamaño : {size:,} bytes\n"
                f"registros: {total}\n"
                f"modificado: {ts}"
            )
        )

        self._card_index.configure(
            text=(
                f"entradas: {len(idx)}\n"
                f"ids: {', '.join(list(idx.keys())[:6])}"
                + (" ..." if len(idx) > 6 else "")
                + f"\narchivo: indice.json"
            )
        )

        hash_short = actual[:24] + "..." if actual else "—"
        self._card_hash.configure(
            text=(
                f"estado : {'ÍNTEGRO ✔' if ok else '¡ALTERADO! ✘'}\n"
                f"hash   : {hash_short}\n"
                f"algoritmo: SHA-256"
            ),
            fg=theme.SUCCESS if ok else theme.DANGER,
        )

        from core.contacto import RECORD_SIZE, FIELD_SIZES
        self._card_sys.configure(
            text=(
                f"reg_size : {RECORD_SIZE} bytes\n"
                f"campos   : {len(FIELD_SIZES)}\n"
                f"id={FIELD_SIZES['id']} nom={FIELD_SIZES['nombre']} tel={FIELD_SIZES['telefono']}\n"
                f"cor={FIELD_SIZES['correo']} ciu={FIELD_SIZES['ciudad']}"
            )
        )

        self.status.set_count(total)

    # ── Navegación ────────────────────────────────────────────────────────────

    def _open_contactos(self) -> None:
        from ui.ventana_contactos import VentanaContactos
        VentanaContactos(self, self.manager, on_change=self._update_stats)

    def _open_exportar(self) -> None:
        from ui.ventana_exportar import VentanaExportar
        VentanaExportar(self, self.manager)

    def _open_herramientas(self) -> None:
        from ui.ventana_herramientas import VentanaHerramientas
        VentanaHerramientas(self, self.manager)

    def _open_ayuda(self) -> None:
        from ui.ventana_ayuda import VentanaAyuda
        VentanaAyuda(self)

    def _salir(self) -> None:
        if messagebox.askyesno("Salir", "¿Cerrar la aplicación?"):
            self.destroy()
