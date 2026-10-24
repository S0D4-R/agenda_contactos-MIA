import json
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from fpdf import FPDF

if TYPE_CHECKING:
    from core.contacto import Contacto


EXPORT_DIR = Path("exports")


class Exportador:
    """
    Genera archivos de exportación a partir de la lista de contactos.
    """
    def __init__(self, export_dir: Path = EXPORT_DIR) -> None:
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    # ── JSON ──────────────────────────────────────────────────────────────────

    def exportar_json(self, contactos: list["Contacto"]) -> Path:
        """
        Exporta todos los contactos a un archivo JSON.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta = self.export_dir / f"contactos_{timestamp}.json"

        payload = {
            "generado_en": datetime.now().isoformat(),
            "total":       len(contactos),
            "contactos":   [c.to_dict() for c in contactos],
        }
        ruta.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return ruta

    # ── PDF ───────────────────────────────────────────────────────────────────

    def exportar_pdf(self, contactos: list["Contacto"]) -> Path:
        """
        Genera un reporte PDF con estética cyberpunk oscura.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta = self.export_dir / f"reporte_{timestamp}.pdf"

        pdf = _CyberpunkPDF()
        pdf.add_page()
        pdf._build_header_section(timestamp, len(contactos))
        pdf._build_table(contactos)
        pdf.output(str(ruta))
        return ruta


# ── Clase PDF interna ─────────────────────────────────────────────────────────

class _CyberpunkPDF(FPDF):
    """PDF con estética cyberpunk: fondo oscuro, tipografía verde neón."""

    # Paleta
    BG      = (10,  10,  20)   # fondo casi negro
    NEON    = (0,   255, 180)  # verde-cyan neón
    ACCENT  = (180, 0,   255)  # magenta/violeta
    WHITE   = (220, 220, 220)
    ROW_A   = (20,  20,  35)   # fila par
    ROW_B   = (28,  28,  50)   # fila impar
    BORDER  = (0,   200, 140)

    def header(self) -> None:
        self.set_fill_color(*self.BG)
        self.rect(0, 0, self.w, self.h, "F")
        # Línea neón superior
        self.set_draw_color(*self.NEON)
        self.set_line_width(0.8)
        self.line(10, 8, self.w - 10, 8)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Courier", "I", 7)
        self.set_text_color(*self.NEON)
        self.cell(0, 5, f"AGENDA_CONTACTOS_v1.0  //  pág. {self.page_no()}",
                  align="C")
        self.set_draw_color(*self.NEON)
        self.set_line_width(0.4)
        self.line(10, self.h - 14, self.w - 10, self.h - 14)

    def _build_header_section(self, ts: str, total: int) -> None:
        self.set_y(14)
        # Título
        self.set_font("Courier", "B", 20)
        self.set_text_color(*self.NEON)
        self.cell(0, 10, "// AGENDA DE CONTACTOS //", align="C", ln=True)
        # Subtítulo
        self.set_font("Courier", "", 9)
        self.set_text_color(*self.ACCENT)
        self.cell(0, 6, f"REPORTE GENERADO: {ts}  |  TOTAL: {total} registros",
                  align="C", ln=True)
        self.ln(4)
        self.set_draw_color(*self.ACCENT)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(4)

    def _build_table(self, contactos: list) -> None:
        # Encabezados
        cols = [("ID", 14), ("NOMBRE", 46), ("TELÉFONO", 30),
                ("CORREO", 62), ("CIUDAD", 28)]

        self.set_font("Courier", "B", 8)
        self.set_fill_color(*self.ACCENT)
        self.set_text_color(*self.BG)
        for label, w in cols:
            self.cell(w, 7, f" {label}", border=0, fill=True)
        self.ln()

        self.set_font("Courier", "", 7)
        for i, c in enumerate(contactos):
            fill_color = self.ROW_A if i % 2 == 0 else self.ROW_B
            self.set_fill_color(*fill_color)
            self.set_text_color(*self.WHITE)

            row = [
                (str(c.id),       14),
                (c.nombre[:28],   46),
                (c.telefono[:18], 30),
                (c.correo[:38],   62),
                (c.ciudad[:17],   28),
            ]
            for val, w in row:
                self.cell(w, 6, f" {val}", border=0, fill=True)
            self.ln()

            # Línea separadora fina
            self.set_draw_color(*self.BORDER)
            self.set_line_width(0.1)
            self.line(10, self.get_y(), self.w - 10, self.get_y())
