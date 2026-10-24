import tkinter as tk
from ui import theme
from ui.widgets import CyberpunkButton, SectionTitle


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
    offset = N × RECORD_SIZE
    f.seek(offset)          ← posicionamiento directo
    pos = f.tell()          ← verificación de posición
    data = f.read(111)      ← lectura exacta

  La modificación es in-place: sólo se sobrescribe
  el registro afectado; el resto del archivo queda intacto.

ÍNDICE PRIMARIO (indice.json)
───────────────────────────────────────────────────
  Estructura: { "id": numero_de_registro, ... }
  Las búsquedas por ID consultan primero el índice
  (O(1)) y luego hacen seek() al byte exacto, evitando
  recorrer el archivo completo (O(n)).

INTEGRIDAD SHA-256
───────────────────────────────────────────────────
  Cada escritura recalcula el SHA-256 del archivo y
  lo guarda en contactos.sha256. Al iniciar, se
  compara; si difiere, se alerta al usuario.

ARCHIVOS GENERADOS
───────────────────────────────────────────────────
  data/contactos.dat        ← registros de tamaño fijo
  data/indice.json          ← índice id → num. registro
  data/contactos.sha256     ← hash de integridad
  exports/contactos_*.json  ← exportaciones JSON
  exports/reporte_*.pdf     ← reportes PDF
  backups/respaldo_*.zip    ← respaldos comprimidos

MÓDULOS UTILIZADOS
───────────────────────────────────────────────────
  hashlib   → SHA-256 para verificación de integridad
  zipfile   → Creación de respaldos comprimidos
  json      → Índice primario y exportación
  os.stat   → Metadatos del archivo
  os.access → Verificación de permisos
  fpdf2     → Generación de reportes PDF
  tkinter   → Interfaz gráfica

═══════════════════════════════════════════════════════════
"""


class VentanaAyuda(tk.Toplevel):
    """Ventana de ayuda con contenido del manual de usuario."""

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.title("◈ AYUDA ◈")
        self.configure(bg=theme.BG_DEEP)
        self.geometry("720x580")
        self.resizable(False, True)
        self._build_ui()

    def _build_ui(self) -> None:
        # Cabecera
        hdr = tk.Frame(self, bg=theme.BG_DEEP, pady=theme.PAD_MD)
        hdr.pack(fill="x", padx=theme.PAD_LG)
        tk.Label(
            hdr, text="// MANUAL DE USUARIO",
            font=theme.FONT_MONO_XL,
            fg=theme.NEON_CYAN, bg=theme.BG_DEEP,
        ).pack(side="left")
        tk.Frame(self, bg=theme.BORDER_NEON, height=1).pack(
            fill="x", padx=theme.PAD_LG
        )

        # Text box de solo lectura
        body = tk.Frame(self, bg=theme.BG_DEEP)
        body.pack(fill="both", expand=True, padx=theme.PAD_LG,
                  pady=theme.PAD_MD)

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

        # Botón cerrar
        btn_row = tk.Frame(self, bg=theme.BG_DEEP, pady=theme.PAD_SM)
        btn_row.pack()
        CyberpunkButton(
            btn_row, "✕  CERRAR", command=self.destroy, variant="ghost"
        ).pack()
