"""
ui/theme.py
===========
Sistema de tokens de diseño cyberpunk para Tkinter.

Paleta:
  BG_DEEP    #050510   fondo base, casi negro-azul
  BG_PANEL   #0D0D1A   paneles secundarios
  BG_CARD    #12122A   tarjetas / entradas
  NEON_CYAN  #00FFB4   acento primario (verde-cyan)
  NEON_MAGENTA #C000FF acento secundario (violeta neón)
  NEON_PINK  #FF00AA   hover / énfasis puntual
  TEXT_MAIN  #E0E0F0   texto principal
  TEXT_DIM   #6E6E9A   texto apagado / placeholder
  BORDER     #1A1A3A   borde sutil
  BORDER_NEON #00FFB4  borde activo
  DANGER     #FF3C5A   error / alerta
  SUCCESS    #00FFB4   confirmación

Tipografía: Courier (monospace del sistema, disponible en todos los SO)
"""

# ── Paleta ────────────────────────────────────────────────────────────────────
BG_DEEP      = "#050510"
BG_PANEL     = "#0D0D1A"
BG_CARD      = "#12122A"
NEON_CYAN    = "#00FFB4"
NEON_MAGENTA = "#C000FF"
NEON_PINK    = "#FF00AA"
TEXT_MAIN    = "#E0E0F0"
TEXT_DIM     = "#5A5A8A"
BORDER       = "#1A1A3A"
BORDER_NEON  = "#00FFB4"
DANGER       = "#FF3C5A"
SUCCESS      = "#00FFB4"
WARNING      = "#FFB400"
WHITE        = "#FFFFFF"

# ── Tipografía ────────────────────────────────────────────────────────────────
FONT_MONO_SM  = ("Courier", 9)
FONT_MONO     = ("Courier", 10)
FONT_MONO_MD  = ("Courier", 11)
FONT_MONO_LG  = ("Courier", 13, "bold")
FONT_MONO_XL  = ("Courier", 16, "bold")
FONT_MONO_XXL = ("Courier", 22, "bold")
FONT_LABEL    = ("Courier", 9)
FONT_TITLE    = ("Courier", 18, "bold")

# ── Geometría ─────────────────────────────────────────────────────────────────
PAD_XS = 4
PAD_SM = 8
PAD_MD = 14
PAD_LG = 20
RADIUS = 0        # Tkinter nativo no soporta border-radius; diseño angular

# ── Configuración base de widgets Tkinter ─────────────────────────────────────

def apply_root_style(root) -> None:
    """Aplica el fondo y el título de la ventana raíz."""
    root.configure(bg=BG_DEEP)


def style_frame(frame, bg=BG_PANEL) -> None:
    frame.configure(bg=bg)


def style_label(label, color=TEXT_MAIN, font=FONT_MONO, bg=BG_PANEL) -> None:
    label.configure(fg=color, bg=bg, font=font)


def style_entry(entry) -> None:
    entry.configure(
        bg=BG_CARD,
        fg=NEON_CYAN,
        insertbackground=NEON_CYAN,
        font=FONT_MONO,
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightcolor=BORDER_NEON,
        highlightbackground=BORDER,
    )


def style_button(
    btn,
    fg=BG_DEEP,
    bg=NEON_CYAN,
    active_bg=NEON_MAGENTA,
    font=FONT_MONO_MD,
) -> None:
    btn.configure(
        fg=fg,
        bg=bg,
        activeforeground=WHITE,
        activebackground=active_bg,
        font=font,
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=PAD_MD,
        pady=PAD_XS,
    )


def style_button_danger(btn) -> None:
    style_button(btn, fg=WHITE, bg=DANGER, active_bg="#FF0040")


def style_button_ghost(btn) -> None:
    style_button(btn, fg=NEON_CYAN, bg=BG_CARD, active_bg=BG_PANEL)


def style_listbox(lb) -> None:
    lb.configure(
        bg=BG_CARD,
        fg=TEXT_MAIN,
        selectbackground=NEON_MAGENTA,
        selectforeground=WHITE,
        font=FONT_MONO_SM,
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightcolor=BORDER_NEON,
        highlightbackground=BORDER,
    )


def style_text(widget) -> None:
    widget.configure(
        bg=BG_CARD,
        fg=NEON_CYAN,
        insertbackground=NEON_CYAN,
        font=FONT_MONO_SM,
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightcolor=BORDER_NEON,
        highlightbackground=BORDER,
    )


def style_scrollbar(sb) -> None:
    sb.configure(
        bg=BG_PANEL,
        troughcolor=BG_DEEP,
        activebackground=NEON_CYAN,
        width=8,
        relief="flat",
        bd=0,
    )


# ── Decoración de texto ───────────────────────────────────────────────────────
SEPARATOR = "─" * 60
GLITCH_CHARS = "▓░▒█"

def neon_title(text: str) -> str:
    return f"◈ {text.upper()} ◈"

def prompt_line(text: str) -> str:
    return f"› {text}"
