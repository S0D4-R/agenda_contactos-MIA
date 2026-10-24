import tkinter as tk
from tkinter import messagebox
from typing import Callable

from core.archivo_manager import ArchivoManager
from core.contacto import Contacto
from ui import theme
from ui.widgets import (
    CyberpunkButton,
    InfoTextBox,
    LabeledEntry,
    SectionTitle,
    ScrollableFrame,
    StatusBar,
)


class VentanaContactos(tk.Toplevel):
    """Gestión completa de contactos con diseño cyberpunk."""

    def __init__(self, parent, manager: ArchivoManager,
                 on_change: Callable | None = None) -> None:
        super().__init__(parent)
        self.manager   = manager
        self.on_change = on_change   # callback para actualizar status en main

        self.title("◈ CONTACTOS ◈")
        self.configure(bg=theme.BG_DEEP)
        self.geometry("960x640")
        self.minsize(800, 500)
        self.resizable(True, True)

        self._selected_id: int | None = None
        self._build_ui()
        self._refresh_list()

    # ── Construcción de la UI ─────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # ── Cabecera ──────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=theme.BG_DEEP, pady=theme.PAD_MD)
        hdr.pack(fill="x", padx=theme.PAD_LG)

        tk.Label(
            hdr, text="// GESTIÓN DE CONTACTOS",
            font=theme.FONT_MONO_XXL,
            fg=theme.NEON_CYAN, bg=theme.BG_DEEP,
        ).pack(side="left")

        sep = tk.Frame(self, bg=theme.BORDER_NEON, height=1)
        sep.pack(fill="x", padx=theme.PAD_LG)

        # ── Layout principal (panel izquierdo + panel derecho) ────────────────
        body = tk.Frame(self, bg=theme.BG_DEEP)
        body.pack(fill="both", expand=True, padx=theme.PAD_LG,
                  pady=theme.PAD_MD)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # Panel derecho: formulario
        self._build_form(body)

        # Panel izquierdo: lista
        self._build_list(body)

        # ── Barra de estado ───────────────────────────────────────────────────
        self.status = StatusBar(self)
        self.status.pack(fill="x", side="bottom")

    def _build_list(self, parent) -> None:
        left = tk.Frame(parent, bg=theme.BG_PANEL)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, theme.PAD_MD))

        SectionTitle(left, "Registros").pack(
            fill="x", padx=theme.PAD_SM, pady=(theme.PAD_SM, 0)
        )

        tk.Frame(left, bg=theme.BORDER, height=1).pack(
            fill="x", padx=theme.PAD_SM
        )

        # Búsqueda rápida
        search_row = tk.Frame(left, bg=theme.BG_PANEL)
        search_row.pack(fill="x", padx=theme.PAD_SM, pady=theme.PAD_XS)

        self._search_var = tk.StringVar()
        search_entry = tk.Entry(search_row, textvariable=self._search_var,
                                width=18)
        theme.style_entry(search_entry)
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))
        search_entry.bind("<Return>", lambda _: self._search_by_id())

        CyberpunkButton(
            search_row, "buscar id", command=self._search_by_id,
            variant="ghost",
        ).pack(side="left")

        # Listbox + scrollbar
        lb_frame = tk.Frame(left, bg=theme.BG_PANEL)
        lb_frame.pack(fill="both", expand=True,
                      padx=theme.PAD_SM, pady=theme.PAD_XS)

        sb = tk.Scrollbar(lb_frame)
        theme.style_scrollbar(sb)
        sb.pack(side="right", fill="y")

        self.listbox = tk.Listbox(lb_frame, yscrollcommand=sb.set,
                                  selectmode="single", activestyle="none")
        theme.style_listbox(self.listbox)
        self.listbox.pack(fill="both", expand=True)
        sb.config(command=self.listbox.yview)

        self.listbox.bind("<<ListboxSelect>>", self._on_list_select)

        # Botones de lista
        btn_row = tk.Frame(left, bg=theme.BG_PANEL, pady=theme.PAD_XS)
        btn_row.pack(fill="x", padx=theme.PAD_SM)

        CyberpunkButton(btn_row, "↺  actualizar",
                        command=self._refresh_list).pack(side="left")

    def _build_form(self, parent) -> None:
        right = tk.Frame(parent, bg=theme.BG_PANEL)
        right.grid(row=0, column=1, sticky="nsew")

        SectionTitle(right, "Formulario").pack(
            fill="x", padx=theme.PAD_SM, pady=(theme.PAD_SM, 0)
        )
        tk.Frame(right, bg=theme.BORDER, height=1).pack(
            fill="x", padx=theme.PAD_SM
        )

        form = tk.Frame(right, bg=theme.BG_PANEL)
        form.pack(fill="both", expand=True, padx=theme.PAD_MD,
                  pady=theme.PAD_MD)

        self._id_entry    = LabeledEntry(form, "ID  (auto / editable)", width=28)
        self._nom_entry   = LabeledEntry(form, "Nombre",   width=28)
        self._tel_entry   = LabeledEntry(form, "Teléfono", width=28)
        self._cor_entry   = LabeledEntry(form, "Correo",   width=28)
        self._ciu_entry   = LabeledEntry(form, "Ciudad",   width=28)

        for w in [self._id_entry, self._nom_entry, self._tel_entry,
                  self._cor_entry, self._ciu_entry]:
            w.pack(fill="x", pady=theme.PAD_XS)

        # ID sugerido
        self._set_suggested_id()

        # Info de posición (seek / tell demo)
        self._pos_var = tk.StringVar(value="pos: —")
        pos_lbl = tk.Label(form, textvariable=self._pos_var,
                           font=theme.FONT_MONO_SM,
                           fg=theme.TEXT_DIM, bg=theme.BG_PANEL)
        pos_lbl.pack(anchor="w", pady=(theme.PAD_XS, 0))

        # Botones de acción
        btn_frame = tk.Frame(right, bg=theme.BG_PANEL)
        btn_frame.pack(fill="x", padx=theme.PAD_MD, pady=(0, theme.PAD_MD))

        CyberpunkButton(
            btn_frame, "◈  AGREGAR", command=self._agregar,
        ).pack(side="left", padx=(0, theme.PAD_XS))

        CyberpunkButton(
            btn_frame, "◉  MODIFICAR", command=self._modificar,
        ).pack(side="left", padx=(0, theme.PAD_XS))

        CyberpunkButton(
            btn_frame, "✕  LIMPIAR",
            command=self._limpiar_form, variant="ghost",
        ).pack(side="left")

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _set_suggested_id(self) -> None:
        self._id_entry.set(str(self.manager.proximo_id()))

    def _limpiar_form(self) -> None:
        self._selected_id = None
        for entry in [self._id_entry, self._nom_entry, self._tel_entry,
                      self._cor_entry, self._ciu_entry]:
            entry.clear()
        self._set_suggested_id()
        self._pos_var.set("pos: —")
        self.status.info("Formulario limpiado.")

    def _read_form(self) -> Contacto | None:
        """Lee y valida los campos del formulario."""
        try:
            id_val = int(self._id_entry.get())
        except ValueError:
            messagebox.showerror("Error", "El ID debe ser un número entero.",
                                 parent=self)
            return None

        nombre   = self._nom_entry.get()
        telefono = self._tel_entry.get()
        correo   = self._cor_entry.get()
        ciudad   = self._ciu_entry.get()

        if not all([nombre, telefono, correo, ciudad]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.",
                                 parent=self)
            return None

        return Contacto(id=id_val, nombre=nombre, telefono=telefono,
                        correo=correo, ciudad=ciudad)

    def _agregar(self) -> None:
        c = self._read_form()
        if c is None:
            return
        try:
            num_reg = self.manager.agregar(c)
            # Mostrar posición usando seek/tell conceptualmente
            offset = num_reg * __import__(
                "core.contacto", fromlist=["RECORD_SIZE"]
            ).RECORD_SIZE
            self._pos_var.set(
                f"seek({offset}) → registro {num_reg}  |  "
                f"tell() = {offset + __import__('core.contacto', fromlist=['RECORD_SIZE']).RECORD_SIZE}"
            )
            self.status.success(
                f"Contacto #{c.id} agregado en posición {num_reg}."
            )
            self._refresh_list()
            self._limpiar_form()
            if self.on_change:
                self.on_change()
        except ValueError as e:
            messagebox.showerror("Error al agregar", str(e), parent=self)
            self.status.error(str(e))

    def _modificar(self) -> None:
        c = self._read_form()
        if c is None:
            return
        if not self.manager.id_existe(c.id):
            messagebox.showerror(
                "No encontrado",
                f"No existe un contacto con ID {c.id}.",
                parent=self,
            )
            return
        if messagebox.askyesno(
            "Confirmar", f"¿Modificar contacto #{c.id}?", parent=self
        ):
            ok = self.manager.modificar(c)
            if ok:
                self.status.success(f"Contacto #{c.id} modificado.")
                self._refresh_list()
                self._limpiar_form()
                if self.on_change:
                    self.on_change()
            else:
                self.status.error("Error al modificar el registro.")

    def _search_by_id(self) -> None:
        raw = self._search_var.get().strip()
        if not raw:
            return
        try:
            id_val = int(raw)
        except ValueError:
            self.status.error("Ingresa un ID numérico para buscar.")
            return

        c = self.manager.buscar_por_id(id_val)
        if c is None:
            self.status.error(f"ID {id_val} no encontrado.")
            messagebox.showinfo(
                "No encontrado", f"No existe contacto con ID {id_val}.",
                parent=self,
            )
            return

        # Cargar en formulario
        self._id_entry.set(str(c.id))
        self._nom_entry.set(c.nombre)
        self._tel_entry.set(c.telefono)
        self._cor_entry.set(c.correo)
        self._ciu_entry.set(c.ciudad)

        idx = self.manager.get_index()
        num_reg = idx.get(str(id_val), "?")
        from core.contacto import RECORD_SIZE
        offset = int(num_reg) * RECORD_SIZE if isinstance(num_reg, int) else "?"
        self._pos_var.set(
            f"seek({offset}) → registro {num_reg}  |  "
            f"tell() = {int(offset) + RECORD_SIZE if isinstance(offset, int) else '?'}"
        )
        self.status.success(f"Contacto #{id_val} cargado desde posición {num_reg}.")

    def _on_list_select(self, event) -> None:
        sel = self.listbox.curselection()
        if not sel:
            return
        text = self.listbox.get(sel[0])
        # Parsear ID del texto "#  123 ..."
        try:
            id_val = int(text.split()[0].lstrip("#"))
        except (ValueError, IndexError):
            return
        c = self.manager.buscar_por_id(id_val)
        if c:
            self._id_entry.set(str(c.id))
            self._nom_entry.set(c.nombre)
            self._tel_entry.set(c.telefono)
            self._cor_entry.set(c.correo)
            self._ciu_entry.set(c.ciudad)

    def _refresh_list(self) -> None:
        self.listbox.delete(0, tk.END)
        contactos = self.manager.listar_todos()
        for c in contactos:
            self.listbox.insert(
                tk.END,
                f"#{c.id:<5}  {c.nombre:<25}  {c.telefono:<15}  {c.ciudad}"
            )
        self.status.set_count(len(contactos))
