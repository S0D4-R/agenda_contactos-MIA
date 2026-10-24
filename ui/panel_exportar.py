import tkinter as tk
from pathlib import Path
from datetime import datetime

from core.archivo_manager import ArchivoManager
from core.exportador import Exportador
from ui import theme
from ui.widgets import CyberpunkButton, InfoTextBox, SectionTitle, StatusBar


class PanelExportar(tk.Frame):
    """Panel de exportación JSON / PDF embebido en el área de tabs."""

    def __init__(self, parent, manager: ArchivoManager, **kwargs) -> None:
        super().__init__(parent, bg=theme.BG_DEEP, **kwargs)
        self.manager    = manager
        self.exportador = Exportador()
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Frame(self, bg=theme.NEON_CYAN, height=2).pack(fill="x")
        tk.Label(
            self, text="  EXPORTACIÓN DE DATOS",
            font=theme.FONT_MONO_LG,
            fg=theme.NEON_CYAN, bg=theme.BG_DEEP,
            anchor="w", pady=10,
        ).pack(fill="x", padx=20)
        tk.Frame(self, bg=theme.BORDER, height=1).pack(fill="x", padx=20)

        body = tk.Frame(self, bg=theme.BG_DEEP)
        body.pack(fill="both", expand=True, padx=20, pady=14)

        # Panel de botones
        opts = tk.Frame(body, bg=theme.BG_PANEL)
        opts.pack(fill="x", pady=(0, 14))

        SectionTitle(opts, "Opciones").pack(
            fill="x", padx=10, pady=(10, 4)
        )
        tk.Frame(opts, bg=theme.BORDER, height=1).pack(fill="x", padx=10)

        btn_row = tk.Frame(opts, bg=theme.BG_PANEL)
        btn_row.pack(pady=14, padx=14, anchor="w")

        CyberpunkButton(
            btn_row, "⬡  EXPORTAR JSON",
            command=self._exportar_json,
        ).pack(side="left", padx=(0, 10))

        CyberpunkButton(
            btn_row, "⬢  GENERAR PDF",
            command=self._exportar_pdf,
        ).pack(side="left")

        # Log
        SectionTitle(body, "Log de exportación", bg=theme.BG_DEEP).pack(
            fill="x", pady=(0, 6)
        )
        self.log = InfoTextBox(body, height=14)
        self.log.pack(fill="both", expand=True)

        self.status = StatusBar(self)
        self.status.pack(fill="x", side="bottom")

        self.log.set_text(
            "[ SISTEMA LISTO ]\nSelecciona una opción para exportar...\n"
        )

    def _exportar_json(self) -> None:
        contactos = self.manager.listar_todos()
        if not contactos:
            self.status.warning("No hay contactos para exportar.")
            return
        try:
            ruta = self.exportador.exportar_json(contactos)
            self._log_ok("JSON", ruta, f"{len(contactos)} registros.")
            self.status.success(f"JSON → {ruta.name}")
        except Exception as e:
            self._log_err("JSON", str(e))
            self.status.error(str(e))

    def _exportar_pdf(self) -> None:
        contactos = self.manager.listar_todos()
        if not contactos:
            self.status.warning("No hay contactos para exportar.")
            return
        try:
            ruta = self.exportador.exportar_pdf(contactos)
            self._log_ok("PDF", ruta,
                         f"{len(contactos)} registros · {ruta.stat().st_size:,} bytes.")
            self.status.success(f"PDF → {ruta.name}")
        except Exception as e:
            self._log_err("PDF", str(e))
            self.status.error(str(e))

    def _log_ok(self, tipo: str, ruta: Path, extra: str = "") -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.append(
            f"\n[{ts}] ✔  {tipo} EXITOSO\n"
            f"         ruta : {ruta}\n"
            f"         info : {extra}\n" + "─" * 55
        )

    def _log_err(self, tipo: str, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.append(
            f"\n[{ts}] ✘  ERROR {tipo}\n"
            f"         {msg}\n" + "─" * 55
        )
