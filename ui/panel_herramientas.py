"""
ui/panel_herramientas.py
========================
Panel embebido de herramientas (tab interno).
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from core.archivo_manager import ArchivoManager
from core.herramientas import Herramientas
from ui import theme
from ui.widgets import CyberpunkButton, InfoTextBox, SectionTitle, StatusBar


class PanelHerramientas(tk.Frame):
    """Panel de herramientas embebido en el área de tabs."""

    def __init__(self, parent, manager: ArchivoManager, **kwargs) -> None:
        super().__init__(parent, bg=theme.BG_DEEP, **kwargs)
        self.manager      = manager
        self.herramientas = Herramientas()
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Frame(self, bg=theme.NEON_CYAN, height=2).pack(fill="x")
        tk.Label(
            self, text="  HERRAMIENTAS DEL SISTEMA",
            font=theme.FONT_MONO_LG,
            fg=theme.NEON_CYAN, bg=theme.BG_DEEP,
            anchor="w", pady=10,
        ).pack(fill="x", padx=20)
        tk.Frame(self, bg=theme.BORDER, height=1).pack(fill="x", padx=20)

        body = tk.Frame(self, bg=theme.BG_DEEP)
        body.pack(fill="both", expand=True, padx=20, pady=14)

        # Botones
        opts = tk.Frame(body, bg=theme.BG_PANEL)
        opts.pack(fill="x", pady=(0, 14))

        SectionTitle(opts, "Operaciones disponibles").pack(
            fill="x", padx=10, pady=(10, 4)
        )
        tk.Frame(opts, bg=theme.BORDER, height=1).pack(fill="x", padx=10)

        btn_row = tk.Frame(opts, bg=theme.BG_PANEL)
        btn_row.pack(pady=14, padx=14, anchor="w")

        CyberpunkButton(
            btn_row, "⚙  VERIFICAR INTEGRIDAD",
            command=self._verificar,
        ).pack(side="left", padx=(0, 8))

        CyberpunkButton(
            btn_row, "◧  CREAR RESPALDO ZIP",
            command=self._respaldar,
        ).pack(side="left", padx=(0, 8))

        CyberpunkButton(
            btn_row, "ℹ  INFO DEL ARCHIVO",
            command=self._info,
        ).pack(side="left")

        # Consola
        SectionTitle(body, "Consola de sistema", bg=theme.BG_DEEP).pack(
            fill="x", pady=(0, 6)
        )
        self.log = InfoTextBox(body, height=15)
        self.log.pack(fill="both", expand=True)

        self.status = StatusBar(self)
        self.status.pack(fill="x", side="bottom")

        self.log.set_text(
            "[ CONSOLA LISTA ]\nSelecciona una operación...\n"
        )

    def _ts(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _verificar(self) -> None:
        ok, guardado, actual = self.manager.verificar_integridad()
        ts = self._ts()
        if ok:
            self.log.append(
                f"\n[{ts}] ✔  INTEGRIDAD VERIFICADA\n"
                f"         guardado : {guardado[:28]}...\n"
                f"         actual   : {actual[:28]}...\n"
                f"         estado   : ÍNTEGRO\n" + "─" * 55
            )
            self.status.success("Archivo íntegro.")
            messagebox.showinfo("Integridad OK",
                                "✔  El archivo no fue modificado externamente.")
        else:
            self.log.append(
                f"\n[{ts}] ✘  ¡INTEGRIDAD COMPROMETIDA!\n"
                f"         guardado : {guardado[:28] if guardado else 'N/A'}...\n"
                f"         actual   : {actual[:28]}...\n"
                f"         ¡Archivo modificado fuera de la app!\n" + "─" * 55
            )
            self.status.error("¡Integridad comprometida!")
            messagebox.showwarning("¡Advertencia!",
                                   "⚠  El hash NO coincide.\n"
                                   "El archivo pudo haber sido alterado externamente.")

    def _respaldar(self) -> None:
        try:
            res = self.herramientas.crear_respaldo(self.manager)
            ts  = self._ts()
            orig_kb = res["tamaño_original"] / 1024
            zip_kb  = res["tamaño_zip"] / 1024
            self.log.append(
                f"\n[{ts}] ✔  RESPALDO CREADO\n"
                f"         archivo   : {res['ruta_zip']}\n"
                f"         original  : {orig_kb:,.2f} KB\n"
                f"         zip       : {zip_kb:,.2f} KB\n"
                f"         reducción : {res['ratio']:.1f}%\n" + "─" * 55
            )
            self.status.success(f"ZIP → {res['ruta_zip'].name}")
            messagebox.showinfo("Respaldo creado",
                                f"Original : {orig_kb:,.2f} KB\n"
                                f"ZIP      : {zip_kb:,.2f} KB\n"
                                f"Reducción: {res['ratio']:.1f}%")
        except Exception as e:
            self.log.append(f"[ ERROR ] {e}")
            self.status.error(str(e))

    def _info(self) -> None:
        info = self.herramientas.obtener_info_archivo(self.manager)
        ts   = self._ts()
        if not info.get("existe"):
            self.log.append(f"[{ts}] ⚠  Archivo de datos no encontrado.\n" + "─"*55)
            self.status.warning("Archivo no encontrado.")
            return
        permisos = []
        if info.get("lectura"):   permisos.append("LECTURA")
        if info.get("escritura"): permisos.append("ESCRITURA")
        self.log.append(
            f"\n[{ts}] ℹ  INFORMACIÓN DEL ARCHIVO\n"
            f"         ruta              : {info['ruta']}\n"
            f"         tamaño            : {info['tamaño_bytes']:,} bytes\n"
            f"         registros         : {info['registros']}\n"
            f"         última modificación: {info['ultima_modificacion']}\n"
            f"         permisos          : {' | '.join(permisos) or 'ninguno'}\n"
            + "─" * 55
        )
        self.status.info("Info cargada.")
