"""
ui/panel_contactos.py
=====================
Panel embebido de gestión de contactos (tab interno).
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable

from core.archivo_manager import ArchivoManager
from core.contacto import Contacto, RECORD_SIZE
from ui import theme
from ui.widgets import CyberpunkButton, LabeledEntry, SectionTitle, StatusBar


class PanelContactos(tk.Frame):
    """Panel con formulario + lista, embebido en el área de tabs."""

    def __init__(self, parent, manager: ArchivoManager,
                 on_change: Callable | None = None, **kwargs) -> None:
        super().__init__(parent, bg=theme.BG_DEEP, **kwargs)
        self.manager   = manager
        self.on_change = on_change
        self._build_ui()
        self._refresh_list()

    def _build_ui(self) -> None:
        # Cabecera del panel
        tk.Frame(self, bg=theme.NEON_CYAN, height=2).pack(fill="x")
        tk.Label(
            self, text="  GESTIÓN DE CONTACTOS",
            font=theme.FONT_MONO_LG,
            fg=theme.NEON_CYAN, bg=theme.BG_DEEP,
            anchor="w", pady=10,
        ).pack(fill="x", padx=20)
        tk.Frame(self, bg=theme.BORDER, height=1).pack(fill="x", padx=20)

        # Layout: lista izquierda | formulario derecha
        body = tk.Frame(self, bg=theme.BG_DEEP)
        body.pack(fill="both", expand=True, padx=20, pady=14)
        body.columnconfigure(0, weight=5)
        body.columnconfigure(1, weight=3)
        body.rowconfigure(0, weight=1)

        self._build_lista(body)
        self._build_formulario(body)

        # Status
        self.status = StatusBar(self)
        self.status.pack(fill="x", side="bottom")

    # ── Lista ─────────────────────────────────────────────────────────────────

    def _build_lista(self, parent) -> None:
        left = tk.Frame(parent, bg=theme.BG_PANEL)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        SectionTitle(left, "Registros").pack(
            fill="x", padx=10, pady=(10, 0)
        )
        tk.Frame(left, bg=theme.BORDER, height=1).pack(fill="x", padx=10)

        # Búsqueda rápida por ID
        search_row = tk.Frame(left, bg=theme.BG_PANEL)
        search_row.pack(fill="x", padx=10, pady=6)

        self._search_var = tk.StringVar()
        se = tk.Entry(search_row, textvariable=self._search_var, width=14)
        theme.style_entry(se)
        se.pack(side="left", fill="x", expand=True, padx=(0, 6))
        se.bind("<Return>", lambda _: self._search_by_id())

        CyberpunkButton(
            search_row, "buscar ID",
            command=self._search_by_id, variant="ghost",
        ).pack(side="left")

        # Listbox
        lb_wrap = tk.Frame(left, bg=theme.BG_PANEL)
        lb_wrap.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        sb = tk.Scrollbar(lb_wrap)
        theme.style_scrollbar(sb)
        sb.pack(side="right", fill="y")

        self.listbox = tk.Listbox(lb_wrap, yscrollcommand=sb.set,
                                  selectmode="single", activestyle="none")
        theme.style_listbox(self.listbox)
        self.listbox.pack(fill="both", expand=True)
        sb.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        CyberpunkButton(
            left, "↺  Actualizar lista",
            command=self._refresh_list,
        ).pack(padx=10, pady=(0, 10), anchor="w")

    # ── Formulario ────────────────────────────────────────────────────────────

    def _build_formulario(self, parent) -> None:
        right = tk.Frame(parent, bg=theme.BG_PANEL)
        right.grid(row=0, column=1, sticky="nsew")

        SectionTitle(right, "Formulario").pack(
            fill="x", padx=10, pady=(10, 0)
        )
        tk.Frame(right, bg=theme.BORDER, height=1).pack(fill="x", padx=10)

        form = tk.Frame(right, bg=theme.BG_PANEL)
        form.pack(fill="both", expand=True, padx=14, pady=10)

        self._f_id  = LabeledEntry(form, "ID  (auto)")
        self._f_nom = LabeledEntry(form, "Nombre")
        self._f_tel = LabeledEntry(form, "Teléfono")
        self._f_cor = LabeledEntry(form, "Correo")
        self._f_ciu = LabeledEntry(form, "Ciudad")

        for w in [self._f_id, self._f_nom, self._f_tel, self._f_cor, self._f_ciu]:
            w.pack(fill="x", pady=4)

        self._set_suggested_id()

        # Indicador seek/tell
        self._pos_var = tk.StringVar(value="seek: —  |  tell: —")
        tk.Label(form, textvariable=self._pos_var,
                 font=theme.FONT_MONO_SM, fg=theme.TEXT_DIM,
                 bg=theme.BG_PANEL, anchor="w").pack(
            fill="x", pady=(4, 0)
        )

        # Botones
        btn_row = tk.Frame(right, bg=theme.BG_PANEL)
        btn_row.pack(fill="x", padx=14, pady=(0, 14))

        CyberpunkButton(btn_row, "◈ AGREGAR",
                        command=self._agregar).pack(side="left", padx=(0, 6))
        CyberpunkButton(btn_row, "◉ MODIFICAR",
                        command=self._modificar).pack(side="left", padx=(0, 6))
        CyberpunkButton(btn_row, "✕ Limpiar",
                        command=self._limpiar, variant="ghost").pack(side="left")

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _set_suggested_id(self) -> None:
        self._f_id.set(str(self.manager.proximo_id()))

    def _limpiar(self) -> None:
        for f in [self._f_id, self._f_nom, self._f_tel, self._f_cor, self._f_ciu]:
            f.clear()
        self._set_suggested_id()
        self._pos_var.set("seek: —  |  tell: —")
        self.status.info("Formulario limpiado.")

    def _read_form(self) -> Contacto | None:
        try:
            id_val = int(self._f_id.get())
        except ValueError:
            messagebox.showerror("Error", "El ID debe ser un número entero.")
            return None
        nombre   = self._f_nom.get()
        telefono = self._f_tel.get()
        correo   = self._f_cor.get()
        ciudad   = self._f_ciu.get()
        if not all([nombre, telefono, correo, ciudad]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return None
        return Contacto(id=id_val, nombre=nombre, telefono=telefono,
                        correo=correo, ciudad=ciudad)

    def _agregar(self) -> None:
        c = self._read_form()
        if not c:
            return
        try:
            num_reg = self.manager.agregar(c)
            offset  = num_reg * RECORD_SIZE
            self._pos_var.set(
                f"seek({offset})  |  tell({offset + RECORD_SIZE})  →  reg {num_reg}"
            )
            self.status.success(f"Contacto #{c.id} agregado en registro {num_reg}.")
            self._refresh_list()
            self._limpiar()
            if self.on_change:
                self.on_change()
        except ValueError as e:
            messagebox.showerror("Error al agregar", str(e))
            self.status.error(str(e))

    def _modificar(self) -> None:
        c = self._read_form()
        if not c:
            return
        if not self.manager.id_existe(c.id):
            messagebox.showerror("No encontrado",
                                 f"No existe contacto con ID {c.id}.")
            return
        if messagebox.askyesno("Confirmar", f"¿Modificar contacto #{c.id}?"):
            if self.manager.modificar(c):
                self.status.success(f"Contacto #{c.id} modificado.")
                self._refresh_list()
                self._limpiar()
                if self.on_change:
                    self.on_change()
            else:
                self.status.error("Error al modificar.")

    def _search_by_id(self) -> None:
        raw = self._search_var.get().strip()
        if not raw:
            return
        try:
            id_val = int(raw)
        except ValueError:
            self.status.error("Ingresa un ID numérico.")
            return
        c = self.manager.buscar_por_id(id_val)
        if not c:
            self.status.error(f"ID {id_val} no encontrado.")
            messagebox.showinfo("No encontrado",
                                f"No existe contacto con ID {id_val}.")
            return
        self._f_id.set(str(c.id));  self._f_nom.set(c.nombre)
        self._f_tel.set(c.telefono); self._f_cor.set(c.correo)
        self._f_ciu.set(c.ciudad)
        num_reg = self.manager.get_index().get(str(id_val), "?")
        offset  = int(num_reg) * RECORD_SIZE if isinstance(num_reg, int) else "?"
        self._pos_var.set(
            f"seek({offset})  |  tell({int(offset)+RECORD_SIZE if isinstance(offset,int) else '?'})  →  reg {num_reg}"
        )
        self.status.success(f"Contacto #{id_val} encontrado.")

    def _on_select(self, _event=None) -> None:
        sel = self.listbox.curselection()
        if not sel:
            return
        try:
            id_val = int(self.listbox.get(sel[0]).split()[0].lstrip("#"))
        except (ValueError, IndexError):
            return
        c = self.manager.buscar_por_id(id_val)
        if c:
            self._f_id.set(str(c.id));   self._f_nom.set(c.nombre)
            self._f_tel.set(c.telefono); self._f_cor.set(c.correo)
            self._f_ciu.set(c.ciudad)

    def _refresh_list(self) -> None:
        self.listbox.delete(0, tk.END)
        for c in self.manager.listar_todos():
            self.listbox.insert(
                tk.END,
                f"#{c.id:<5}  {c.nombre:<26}  {c.telefono:<15}  {c.ciudad}"
            )
        self.status.set_count(self.manager.total_registros())
