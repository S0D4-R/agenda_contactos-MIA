import tkinter as tk
from ui import theme
from ui.widgets import SectionTitle

HELP_CONTENT = """
◈ AGENDA DE CONTACTOS — MANUAL DE USUARIO ◈
═══════════════════════════════════════════════════════════

ESTRUCTURA DEL REGISTRO (tamaño fijo = 111 bytes)
───────────────────────────────────────────────────
  Campo      │ Bytes │ Descripción
  ───────────┼───────┼──────────────────────────────────
  id         │   5   │ Entero único, relleno a derecha
  nombre     │  30   │ Texto, relleno con espacios
  telefono   │  15   │ Texto, relleno con espacios
  correo     │  40   │ Texto, relleno con espacios
  ciudad     │  20   │ Texto, relleno con espacios
  newline    │   1   │ Separador \\n
  ───────────┼───────┼──────────────────────────────────
  TOTAL      │ 111   │ bytes por registro

ACCESO ALEATORIO (seek / tell)
───────────────────────────────────────────────────
  Para leer el registro N:
    offset = N × RECORD_SIZE       (ej. N=2 → offset=222)
    f.seek(offset)                 ← posicionamiento directo
    pos = f.tell()                 ← verificación
    data = f.read(111)             ← lectura exacta

  Modificación in-place:
    with open(dat, "r+b") as f:
        f.seek(num_registro * RECORD_SIZE)
        f.write(contacto.to_record())   ← solo ese registro

ÍNDICE PRIMARIO (indice.json)
───────────────────────────────────────────────────
  Estructura: { "id": numero_registro, ... }
  Búsqueda O(1) vs O(n) secuencial:
    1. Consultar índice → num_registro
    2. seek(num_registro × 111) → leer directamente

INTEGRIDAD SHA-256
───────────────────────────────────────────────────
  Cada escritura recalcula SHA-256 y lo guarda en
  contactos.sha256. Al iniciar se compara; si difiere
  se alerta al usuario.

ARCHIVOS GENERADOS
───────────────────────────────────────────────────
  data/contactos.dat        ← registros de tamaño fijo
  data/indice.json          ← índice id → num. registro
  data/contactos.sha256     ← hash de integridad
  exports/contactos_*.json  ← exportaciones JSON
  exports/reporte_*.pdf     ← reportes PDF
  backups/respaldo_*.zip    ← respaldos comprimidos

MÓDULOS PYTHON UTILIZADOS
───────────────────────────────────────────────────
  hashlib   → SHA-256
  zipfile   → respaldos comprimidos
  json      → índice y exportación
  os.stat   → metadatos del archivo
  os.access → verificación de permisos
  fpdf2     → generación de PDF
  tkinter   → interfaz gráfica

═══════════════════════════════════════════════════════════
"""


class PanelAyuda(tk.Frame):
    """Panel de ayuda embebido en el área de tabs."""

    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, bg=theme.BG_DEEP, **kwargs)
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Frame(self, bg=theme.NEON_CYAN, height=2).pack(fill="x")
        tk.Label(
            self, text="  MANUAL DE USUARIO",
            font=theme.FONT_MONO_LG,
            fg=theme.NEON_CYAN, bg=theme.BG_DEEP,
            anchor="w", pady=10,
        ).pack(fill="x", padx=20)
        tk.Frame(self, bg=theme.BORDER, height=1).pack(fill="x", padx=20)

        body = tk.Frame(self, bg=theme.BG_DEEP)
        body.pack(fill="both", expand=True, padx=20, pady=14)

        sb = tk.Scrollbar(body)
        sb.pack(side="right", fill="y")

        txt = tk.Text(
            body, wrap="word", state="normal",
            font=theme.FONT_MONO_SM,
            bg=theme.BG_CARD, fg=theme.NEON_CYAN,
            insertbackground=theme.NEON_CYAN,
            relief="flat", bd=0,
            highlightthickness=1,
            highlightcolor=theme.BORDER_NEON,
            highlightbackground=theme.BORDER,
            yscrollcommand=sb.set,
        )
        txt.insert("1.0", HELP_CONTENT)
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True)
        sb.config(command=txt.yview)
