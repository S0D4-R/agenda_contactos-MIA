import tkinter as tk
from tkinter import messagebox
from pathlib import Path

from core.archivo_manager import ArchivoManager
from core.exportador import Exportador
from ui import theme
from ui.widgets import CyberpunkButton, InfoTextBox, SectionTitle, StatusBar


class VentanaExportar(tk.Toplevel):
    """Exporta contactos a JSON y/o PDF con feedback visual."""

    def __init__(self, parent, manager: ArchivoManager) -> None:
        super().__init__(parent)
        self.manager    = manager
        self.exportador = Exportador()

        self.title("◈ EXPORTAR ◈")
        self.configure(bg=theme.BG_DEEP)
        self.geometry("700x480")
        self.resizable(False, False)

        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Cabecera
        hdr = tk.Frame(self, bg=theme.BG_DEEP, pady=theme.PAD_MD)
        hdr.pack(fill="x", padx=theme.PAD_LG)
        tk.Label(
            hdr, text="// EXPORTACIÓN DE DATOS",
            font=theme.FONT_MONO_XL,
            fg=theme.NEON_CYAN, bg=theme.BG_DEEP,
        ).pack(side="left")

        tk.Frame(self, bg=theme.BORDER_NEON, height=1).pack(
            fill="x", padx=theme.PAD_LG
        )

        # Cuerpo
        body = tk.Frame(self, bg=theme.BG_DEEP)
        body.pack(fill="both", expand=True, padx=theme.PAD_LG,
                  pady=theme.PAD_MD)

        # Panel de opciones
        options = tk.Frame(body, bg=theme.BG_PANEL)
        options.pack(fill="x", pady=(0, theme.PAD_MD))

        SectionTitle(options, "Opciones de exportación").pack(
            fill="x", padx=theme.PAD_SM, pady=(theme.PAD_SM, theme.PAD_XS)
        )
        tk.Frame(options, bg=theme.BORDER, height=1).pack(fill="x",
                                                           padx=theme.PAD_SM)

        btn_row = tk.Frame(options, bg=theme.BG_PANEL)
        btn_row.pack(pady=theme.PAD_MD, padx=theme.PAD_MD)

        CyberpunkButton(
            btn_row, "⬡  EXPORTAR JSON",
            command=self._exportar_json,
        ).pack(side="left", padx=theme.PAD_SM)

        CyberpunkButton(
            btn_row, "⬢  GENERAR PDF",
            command=self._exportar_pdf,
        ).pack(side="left", padx=theme.PAD_SM)

        # Log de resultados
        SectionTitle(body, "Log de exportación", bg=theme.BG_DEEP).pack(
            fill="x", pady=(0, theme.PAD_XS)
        )
        self.log = InfoTextBox(body, height=12)
        self.log.pack(fill="both", expand=True)

        # Status bar
        self.status = StatusBar(self)
        self.status.pack(fill="x", side="bottom")

        self.log.set_text(
            "[ SISTEMA LISTO ]\n"
            "Selecciona una opción de exportación para continuar...\n"
        )

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _exportar_json(self) -> None:
        contactos = self.manager.listar_todos()
        if not contactos:
            messagebox.showwarning(
                "Sin datos", "No hay contactos para exportar.", parent=self
            )
            return
        try:
            ruta = self.exportador.exportar_json(contactos)
            self._log_success(
                "JSON",
                ruta,
                f"{len(contactos)} registros exportados.",
            )
            self.status.success(f"JSON generado: {ruta.name}")
        except Exception as e:
            self._log_error("JSON", str(e))
            self.status.error(str(e))

    def _exportar_pdf(self) -> None:
        contactos = self.manager.listar_todos()
        if not contactos:
            messagebox.showwarning(
                "Sin datos", "No hay contactos para exportar.", parent=self
            )
            return
        try:
            ruta = self.exportador.exportar_pdf(contactos)
            self._log_success(
                "PDF",
                ruta,
                f"{len(contactos)} registros · {ruta.stat().st_size:,} bytes.",
            )
            self.status.success(f"PDF generado: {ruta.name}")
        except Exception as e:
            self._log_error("PDF", str(e))
            self.status.error(str(e))

    def _log_success(self, tipo: str, ruta: Path, extra: str = "") -> None:
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.append(
            f"\n[{ts}] ✔  EXPORTACIÓN {tipo} EXITOSA\n"
            f"         ruta : {ruta}\n"
            f"         info : {extra}\n"
            + "─" * 55
        )

    def _log_error(self, tipo: str, msg: str) -> None:
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.append(
            f"\n[{ts}] ✘  ERROR EN EXPORTACIÓN {tipo}\n"
            f"         error: {msg}\n"
            + "─" * 55
        )
