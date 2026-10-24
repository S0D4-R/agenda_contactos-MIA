"""
ui/app.py
=========
Ventana principal — layout de tabs interno (sin ventanas secundarias).
Sidebar de navegación + área de contenido que cambia según el tab activo.
"""

import tkinter as tk
from tkinter import messagebox

from core.archivo_manager import ArchivoManager
from ui import theme
from ui.widgets import CyberpunkButton, StatusBar


class App(tk.Tk):
    """
    Ventana raíz con navegación lateral y contenido en tabs.
    Cada sección (Contactos, Exportar, Herramientas, Ayuda, Dashboard)
    se renderiza dentro del mismo panel derecho sin abrir ventanas nuevas.
    """

    def __init__(self) -> None:
        super().__init__()
        self.manager = ArchivoManager()
        self._check_integrity_on_start()

        self.title("◈ AGENDA DE CONTACTOS — ACCESO ALEATORIO ◈")
        self.configure(bg=theme.BG_DEEP)
        self.geometry("1100x700")
        self.minsize(900, 560)
        self.resizable(True, True)

        # Refs a los botones de nav para resaltar el activo
        self._nav_buttons: dict[str, tk.Button] = {}
        # Frame contenedor de cada tab (se crean lazy)
        self._tab_frames:  dict[str, tk.Frame]  = {}
        self._active_tab = ""

        self._build_ui()
        self._show_tab("dashboard")

    # ── Integridad al inicio ──────────────────────────────────────────────────

    def _check_integrity_on_start(self) -> None:
        self.manager.inicializar_hash_si_falta()
        ok, _, _ = self.manager.verificar_integridad()
        if not ok:
            messagebox.showwarning(
                "⚠  Advertencia de integridad",
                "El archivo de contactos fue modificado fuera de la aplicación.\n"
                "Verifica la integridad desde Herramientas.",
            )

    # ── Esqueleto principal ───────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Banda neón top
        tk.Frame(self, bg=theme.NEON_CYAN, height=3).pack(fill="x")

        # Header
        self._build_header()

        # Línea separadora
        tk.Frame(self, bg=theme.NEON_MAGENTA, height=1).pack(fill="x")

        # Body: sidebar izquierdo + área de contenido derecha
        body = tk.Frame(self, bg=theme.BG_DEEP)
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)
        self._build_content_area(body)

        # Status bar
        tk.Frame(self, bg=theme.BORDER, height=1).pack(fill="x")
        self.status = StatusBar(self)
        self.status.pack(fill="x", side="bottom")

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self) -> None:
        hdr = tk.Frame(self, bg=theme.BG_DEEP, pady=14)
        hdr.pack(fill="x", padx=20)

        # Título
        left = tk.Frame(hdr, bg=theme.BG_DEEP)
        left.pack(side="left")

        tk.Label(
            left, text="AGENDA",
            font=("Courier", 34, "bold"),
            fg=theme.NEON_CYAN, bg=theme.BG_DEEP,
        ).pack(anchor="w")
        tk.Label(
            left, text="DE CONTACTOS  //  ACCESO ALEATORIO",
            font=("Courier", 12),
            fg=theme.NEON_MAGENTA, bg=theme.BG_DEEP,
        ).pack(anchor="w")

        # Stats
        right = tk.Frame(hdr, bg=theme.BG_DEEP)
        right.pack(side="right")
        self._stat_registros  = self._stat_block(right, "REGISTROS", "0")
        self._stat_archivo    = self._stat_block(right, "ARCHIVO",   "—")
        self._stat_integridad = self._stat_block(right, "INTEGRIDAD","—")

    def _stat_block(self, parent, label: str, value: str) -> tk.Label:
        f = tk.Frame(parent, bg=theme.BG_CARD, padx=16, pady=6)
        f.pack(side="left", padx=4)
        tk.Label(f, text=label, font=theme.FONT_LABEL,
                 fg=theme.TEXT_DIM, bg=theme.BG_CARD).pack()
        lbl = tk.Label(f, text=value, font=theme.FONT_MONO_LG,
                       fg=theme.NEON_CYAN, bg=theme.BG_CARD)
        lbl.pack()
        return lbl

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self, parent) -> None:
        side = tk.Frame(parent, bg=theme.BG_PANEL, width=220)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        tk.Frame(side, bg=theme.NEON_CYAN, height=2).pack(fill="x")
        tk.Label(
            side, text="  NAVEGACIÓN",
            font=theme.FONT_MONO_MD,
            fg=theme.NEON_CYAN, bg=theme.BG_PANEL,
            anchor="w", pady=10,
        ).pack(fill="x")
        tk.Frame(side, bg=theme.BORDER, height=1).pack(fill="x")

        tabs = [
            ("dashboard",    "⬛  DASHBOARD"),
            ("contactos",    "◈  CONTACTOS"),
            ("exportar",     "⬡  EXPORTAR"),
            ("herramientas", "⚙  HERRAMIENTAS"),
            ("ayuda",        "ℹ  AYUDA"),
        ]
        for key, label in tabs:
            btn = tk.Button(
                side, text=label,
                font=theme.FONT_MONO_MD,
                fg=theme.TEXT_MAIN, bg=theme.BG_PANEL,
                activeforeground=theme.BG_DEEP,
                activebackground=theme.NEON_CYAN,
                relief="flat", bd=0, anchor="w",
                padx=16, pady=10, cursor="hand2",
                command=lambda k=key: self._show_tab(k),
            )
            btn.pack(fill="x")
            self._nav_buttons[key] = btn

        # Separador + botón salir al fondo
        tk.Frame(side, bg=theme.BORDER, height=1).pack(fill="x", pady=(20, 0))
        quit_btn = tk.Button(
            side, text="✕  SALIR",
            font=theme.FONT_MONO_MD,
            fg=theme.DANGER, bg=theme.BG_PANEL,
            activeforeground=theme.WHITE,
            activebackground=theme.DANGER,
            relief="flat", bd=0, anchor="w",
            padx=16, pady=10, cursor="hand2",
            command=self._salir,
        )
        quit_btn.pack(fill="x")

        tk.Label(
            side, text="\n  v1.0.0 // 2026\n  URL Quetzaltenango",
            font=("Courier", 9),
            fg=theme.TEXT_DIM, bg=theme.BG_PANEL,
            anchor="w", justify="left",
        ).pack(fill="x", side="bottom", padx=8, pady=8)

    # ── Área de contenido ─────────────────────────────────────────────────────

    def _build_content_area(self, parent) -> None:
        self._content = tk.Frame(parent, bg=theme.BG_DEEP)
        self._content.pack(side="left", fill="both", expand=True)

    # ── Sistema de tabs ───────────────────────────────────────────────────────

    def _show_tab(self, key: str) -> None:
        # Ocultar tab anterior
        if self._active_tab and self._active_tab in self._tab_frames:
            self._tab_frames[self._active_tab].pack_forget()

        # Actualizar aspecto de botones nav
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.configure(
                    bg=theme.NEON_CYAN,
                    fg=theme.BG_DEEP,
                    font=(*theme.FONT_MONO_MD[:2], "bold"),
                )
            else:
                btn.configure(
                    bg=theme.BG_PANEL,
                    fg=theme.TEXT_MAIN,
                    font=theme.FONT_MONO_MD,
                )

        # Crear frame si no existe
        if key not in self._tab_frames:
            frame = tk.Frame(self._content, bg=theme.BG_DEEP)
            self._tab_frames[key] = frame
            builder = getattr(self, f"_build_tab_{key}")
            builder(frame)

        self._tab_frames[key].pack(fill="both", expand=True)
        self._active_tab = key

        # Refrescar stats siempre que sea dashboard o al volver
        if key == "dashboard":
            self._update_stats()

    # ══════════════════════════════════════════════════════════════════════════
    # TABS
    # ══════════════════════════════════════════════════════════════════════════

    # ── Tab: Dashboard ────────────────────────────────────────────────────────

    def _build_tab_dashboard(self, parent) -> None:
        tk.Frame(parent, bg=theme.NEON_MAGENTA, height=2).pack(fill="x")
        tk.Label(
            parent, text="  DASHBOARD DEL SISTEMA",
            font=theme.FONT_MONO_LG,
            fg=theme.NEON_MAGENTA, bg=theme.BG_DEEP,
            anchor="w", pady=10,
        ).pack(fill="x", padx=20)
        tk.Frame(parent, bg=theme.BORDER, height=1).pack(fill="x", padx=20)

        cards = tk.Frame(parent, bg=theme.BG_DEEP)
        cards.pack(fill="both", expand=True, padx=20, pady=14)
        cards.columnconfigure(0, weight=1)
        cards.columnconfigure(1, weight=1)
        cards.rowconfigure(0, weight=1)
        cards.rowconfigure(1, weight=1)

        self._card_dat   = self._info_card(cards, "ARCHIVO DE DATOS", 0, 0)
        self._card_index = self._info_card(cards, "ÍNDICE PRIMARIO",  0, 1)
        self._card_hash  = self._info_card(cards, "HASH SHA-256",     1, 0)
        self._card_sys   = self._info_card(cards, "ESTRUCTURA",       1, 1)

        # Accesos rápidos
        quick = tk.Frame(parent, bg=theme.BG_DEEP)
        quick.pack(fill="x", padx=20, pady=(0, 14))
        tk.Label(quick, text="ACCESOS RÁPIDOS", font=theme.FONT_LABEL,
                 fg=theme.TEXT_DIM, bg=theme.BG_DEEP, anchor="w").pack(fill="x")
        q_row = tk.Frame(quick, bg=theme.BG_DEEP)
        q_row.pack(fill="x", pady=6)
        for label, key in [
            ("+ Agregar",    "contactos"),
            ("⌕ Buscar ID",  "contactos"),
            ("↺ Respaldar",  "herramientas"),
            ("⬡ Exportar",   "exportar"),
        ]:
            CyberpunkButton(
                q_row, label,
                command=lambda k=key: self._show_tab(k),
                variant="ghost",
            ).pack(side="left", padx=(0, 8))

    def _info_card(self, parent, title: str, row: int, col: int) -> tk.Label:
        card = tk.Frame(parent, bg=theme.BG_CARD, padx=12, pady=10)
        card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
        tk.Label(card, text=title, font=theme.FONT_LABEL,
                 fg=theme.TEXT_DIM, bg=theme.BG_CARD, anchor="w").pack(fill="x")
        tk.Frame(card, bg=theme.BORDER, height=1).pack(fill="x", pady=(2, 6))
        lbl = tk.Label(card, text="cargando...", font=theme.FONT_MONO_SM,
                       fg=theme.TEXT_MAIN, bg=theme.BG_CARD,
                       anchor="w", justify="left")
        lbl.pack(fill="x")
        return lbl

    # ── Tab: Contactos ────────────────────────────────────────────────────────

    def _build_tab_contactos(self, parent) -> None:
        from ui.panel_contactos import PanelContactos
        PanelContactos(parent, self.manager,
                       on_change=self._update_stats).pack(fill="both", expand=True)

    # ── Tab: Exportar ─────────────────────────────────────────────────────────

    def _build_tab_exportar(self, parent) -> None:
        from ui.panel_exportar import PanelExportar
        PanelExportar(parent, self.manager).pack(fill="both", expand=True)

    # ── Tab: Herramientas ─────────────────────────────────────────────────────

    def _build_tab_herramientas(self, parent) -> None:
        from ui.panel_herramientas import PanelHerramientas
        PanelHerramientas(parent, self.manager).pack(fill="both", expand=True)

    # ── Tab: Ayuda ────────────────────────────────────────────────────────────

    def _build_tab_ayuda(self, parent) -> None:
        from ui.panel_ayuda import PanelAyuda
        PanelAyuda(parent).pack(fill="both", expand=True)

    # ── Stats ─────────────────────────────────────────────────────────────────

    def _update_stats(self) -> None:
        info = self.manager.info_archivo()
        idx  = self.manager.get_index()
        ok, _, actual = self.manager.verificar_integridad()

        total = info.get("registros", 0)
        size  = info.get("tamaño_bytes", 0)
        ts    = info.get("ultima_modificacion", "—")

        self._stat_registros.configure(text=str(total))
        self._stat_archivo.configure(
            text=f"{size/1024:.1f} KB" if size else "0 KB"
        )
        self._stat_integridad.configure(
            text="OK" if ok else "⚠",
            fg=theme.SUCCESS if ok else theme.DANGER,
        )

        if hasattr(self, "_card_dat"):
            self._card_dat.configure(
                text=(
                    f"ruta      : {info.get('ruta','—')}\n"
                    f"tamaño    : {size:,} bytes\n"
                    f"registros : {total}\n"
                    f"modificado: {ts}"
                )
            )
            self._card_index.configure(
                text=(
                    f"entradas : {len(idx)}\n"
                    f"ids      : {', '.join(list(idx.keys())[:5])}"
                    + (" ..." if len(idx) > 5 else "") + "\n"
                    f"archivo  : indice.json"
                )
            )
            hash_short = actual[:22] + "..." if actual else "—"
            self._card_hash.configure(
                text=(
                    f"estado    : {'ÍNTEGRO ✔' if ok else '¡ALTERADO! ✘'}\n"
                    f"hash      : {hash_short}\n"
                    f"algoritmo : SHA-256"
                ),
                fg=theme.SUCCESS if ok else theme.DANGER,
            )
            from core.contacto import RECORD_SIZE, FIELD_SIZES
            self._card_sys.configure(
                text=(
                    f"reg_size : {RECORD_SIZE} bytes\n"
                    f"campos   : {len(FIELD_SIZES)}\n"
                    f"id={FIELD_SIZES['id']} nom={FIELD_SIZES['nombre']} "
                    f"tel={FIELD_SIZES['telefono']}\n"
                    f"cor={FIELD_SIZES['correo']} ciu={FIELD_SIZES['ciudad']}"
                )
            )
        self.status.set_count(total)

    # ── Salir ─────────────────────────────────────────────────────────────────

    def _salir(self) -> None:
        if messagebox.askyesno("Salir", "¿Cerrar la aplicación?"):
            self.destroy()
