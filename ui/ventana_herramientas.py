"""
ui/ventana_herramientas.py
==========================
Ventana de herramientas:
  - Verificar integridad SHA-256
  - Crear respaldo ZIP
  - Información del archivo
"""

import tkinter as tk
from tkinter import messagebox

from core.archivo_manager import ArchivoManager
from core.herramientas import Herramientas
from ui import theme
from ui.widgets import CyberpunkButton, InfoTextBox, SectionTitle, StatusBar


class VentanaHerramientas(tk.Toplevel):
    """Panel de herramientas del sistema con estilo cyberpunk."""

    def __init__(self, parent, manager: ArchivoManager) -> None:
        super().__init__(parent)
        self.manager     = manager
        self.herramientas = Herramientas()

        self.title("◈ HERRAMIENTAS ◈")
        self.configure(bg=theme.BG_DEEP)
        self.geometry("750x560")
        self.resizable(False, True)

        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Cabecera
        hdr = tk.Frame(self, bg=theme.BG_DEEP, pady=theme.PAD_MD)
        hdr.pack(fill="x", padx=theme.PAD_LG)
        tk.Label(
            hdr, text="// HERRAMIENTAS DEL SISTEMA",
            font=theme.FONT_MONO_XL,
            fg=theme.NEON_CYAN, bg=theme.BG_DEEP,
        ).pack(side="left")
        tk.Frame(self, bg=theme.BORDER_NEON, height=1).pack(
            fill="x", padx=theme.PAD_LG
        )

        body = tk.Frame(self, bg=theme.BG_DEEP)
        body.pack(fill="both", expand=True, padx=theme.PAD_LG,
                  pady=theme.PAD_MD)

        # Botones de herramientas
        btn_panel = tk.Frame(body, bg=theme.BG_PANEL)
        btn_panel.pack(fill="x", pady=(0, theme.PAD_MD))

        SectionTitle(btn_panel, "Operaciones").pack(
            fill="x", padx=theme.PAD_SM,
            pady=(theme.PAD_SM, theme.PAD_XS),
        )
        tk.Frame(btn_panel, bg=theme.BORDER, height=1).pack(
            fill="x", padx=theme.PAD_SM
        )

        btn_row = tk.Frame(btn_panel, bg=theme.BG_PANEL)
        btn_row.pack(pady=theme.PAD_MD, padx=theme.PAD_MD)

        CyberpunkButton(
            btn_row, "⚙  VERIFICAR INTEGRIDAD",
            command=self._verificar_integridad,
        ).pack(side="left", padx=theme.PAD_XS)

        CyberpunkButton(
            btn_row, "◧  CREAR RESPALDO ZIP",
            command=self._crear_respaldo,
        ).pack(side="left", padx=theme.PAD_XS)

        CyberpunkButton(
            btn_row, "ℹ  INFO DEL ARCHIVO",
            command=self._info_archivo,
        ).pack(side="left", padx=theme.PAD_XS)

        # Log
        SectionTitle(body, "Consola de sistema", bg=theme.BG_DEEP).pack(
            fill="x", pady=(0, theme.PAD_XS)
        )
        self.log = InfoTextBox(body, height=16)
        self.log.pack(fill="both", expand=True)

        self.status = StatusBar(self)
        self.status.pack(fill="x", side="bottom")

        self.log.set_text(
            "[ CONSOLA DE HERRAMIENTAS ]\n"
            "Selecciona una operación para ejecutar...\n"
        )

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _verificar_integridad(self) -> None:
        ok, guardado, actual = self.manager.verificar_integridad()
        ts = self._ts()

        if ok:
            msg = (
                f"[{ts}] ✔  INTEGRIDAD VERIFICADA\n"
                f"         SHA-256 guardado : {guardado[:32]}...\n"
                f"         SHA-256 actual   : {actual[:32]}...\n"
                f"         estado : ÍNTEGRO — sin modificaciones externas\n"
                + "─" * 58
            )
            self.log.append(msg)
            self.status.success("Archivo íntegro.")
            messagebox.showinfo(
                "Integridad OK",
                "✔  El archivo de contactos no ha sido modificado externamente.",
                parent=self,
            )
        else:
            msg = (
                f"[{ts}] ✘  ADVERTENCIA: INTEGRIDAD COMPROMETIDA\n"
                f"         SHA-256 guardado : {guardado[:32] if guardado else 'N/A'}...\n"
                f"         SHA-256 actual   : {actual[:32]}...\n"
                f"         ¡El archivo fue modificado fuera de la aplicación!\n"
                + "─" * 58
            )
            self.log.append(msg)
            self.status.error("¡Integridad comprometida!")
            messagebox.showwarning(
                "¡Advertencia de integridad!",
                "⚠  El hash del archivo NO coincide.\n\n"
                "El archivo de contactos pudo haber sido modificado\n"
                "fuera de esta aplicación.",
                parent=self,
            )

    def _crear_respaldo(self) -> None:
        try:
            res = self.herramientas.crear_respaldo(self.manager)
            ts  = self._ts()
            orig_kb = res["tamaño_original"] / 1024
            zip_kb  = res["tamaño_zip"] / 1024
            msg = (
                f"[{ts}] ✔  RESPALDO ZIP CREADO\n"
                f"         archivo  : {res['ruta_zip']}\n"
                f"         original : {orig_kb:,.2f} KB\n"
                f"         zip      : {zip_kb:,.2f} KB\n"
                f"         reducción: {res['ratio']:.1f}%\n"
                + "─" * 58
            )
            self.log.append(msg)
            self.status.success(f"Respaldo creado: {res['ruta_zip'].name}")
            messagebox.showinfo(
                "Respaldo creado",
                f"◧  Respaldo generado exitosamente.\n\n"
                f"Tamaño original : {orig_kb:,.2f} KB\n"
                f"Tamaño ZIP      : {zip_kb:,.2f} KB\n"
                f"Reducción       : {res['ratio']:.1f}%",
                parent=self,
            )
        except Exception as e:
            self.log.append(f"[ ERROR ] {e}")
            self.status.error(str(e))

    def _info_archivo(self) -> None:
        info = self.herramientas.obtener_info_archivo(self.manager)
        ts = self._ts()

        if not info.get("existe"):
            self.log.append(
                f"[{ts}] ⚠  Archivo de datos no encontrado.\n" + "─" * 58
            )
            self.status.warning("Archivo no encontrado.")
            return

        permisos = []
        if info.get("lectura"):  permisos.append("LECTURA")
        if info.get("escritura"): permisos.append("ESCRITURA")

        msg = (
            f"[{ts}] ℹ  INFORMACIÓN DEL ARCHIVO\n"
            f"         ruta             : {info['ruta']}\n"
            f"         tamaño           : {info['tamaño_bytes']:,} bytes\n"
            f"         registros        : {info['registros']}\n"
            f"         última modificación: {info['ultima_modificacion']}\n"
            f"         permisos         : {' | '.join(permisos) or 'ninguno'}\n"
            + "─" * 58
        )
        self.log.append(msg)
        self.status.info("Info del archivo cargada.")

    @staticmethod
    def _ts() -> str:
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
