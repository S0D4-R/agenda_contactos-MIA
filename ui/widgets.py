"""
ui/widgets.py
=============
Componentes Tkinter reutilizables con estilo cyberpunk.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from ui import theme


class NeonFrame(tk.Frame):
    """Frame con borde neón simulado mediante un Frame exterior."""

    def __init__(
        self,
        parent,
        border_color: str = theme.BORDER_NEON,
        bg: str = theme.BG_PANEL,
        **kwargs,
    ) -> None:
        # Outer frame = color del borde
        outer = tk.Frame(parent, bg=border_color, padx=1, pady=1)
        outer.pack_propagate(False)

        super().__init__(outer, bg=bg, **kwargs)
        super().pack(fill="both", expand=True)

        # Exponemos el frame exterior para que el usuario lo posicione
        self.outer = outer

    def pack(self, **kwargs):
        self.outer.pack(**kwargs)

    def grid(self, **kwargs):
        self.outer.grid(**kwargs)

    def place(self, **kwargs):
        self.outer.place(**kwargs)


class LabeledEntry(tk.Frame):
    """Label + Entry en columna con estilo cyberpunk."""

    def __init__(
        self,
        parent,
        label_text: str,
        width: int = 30,
        **kwargs,
    ) -> None:
        super().__init__(parent, bg=theme.BG_PANEL, **kwargs)

        lbl = tk.Label(self, text=f"  {label_text}", anchor="w")
        theme.style_label(lbl, color=theme.TEXT_DIM, font=theme.FONT_LABEL)
        lbl.pack(fill="x")

        self.entry = tk.Entry(self, width=width)
        theme.style_entry(self.entry)
        self.entry.pack(fill="x", pady=(0, theme.PAD_XS))

    def get(self) -> str:
        return self.entry.get().strip()

    def set(self, value: str) -> None:
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)

    def clear(self) -> None:
        self.entry.delete(0, tk.END)

    def focus(self) -> None:
        self.entry.focus_set()


class CyberpunkButton(tk.Button):
    """Botón principal con hover animado."""

    def __init__(
        self,
        parent,
        text: str,
        command: Optional[Callable] = None,
        variant: str = "primary",   # primary | danger | ghost
        **kwargs,
    ) -> None:
        super().__init__(parent, text=text, command=command, **kwargs)
        if variant == "danger":
            theme.style_button_danger(self)
        elif variant == "ghost":
            theme.style_button_ghost(self)
        else:
            theme.style_button(self)

        self._bg     = self.cget("bg")
        self._fg     = self.cget("fg")
        self._hov_bg = theme.NEON_MAGENTA if variant == "primary" else theme.NEON_PINK

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event=None) -> None:
        self.configure(bg=self._hov_bg, fg=theme.WHITE)

    def _on_leave(self, _event=None) -> None:
        self.configure(bg=self._bg, fg=self._fg)


class StatusBar(tk.Frame):
    """Barra de estado con mensaje coloreado y contador."""

    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, bg=theme.BG_DEEP, height=24, **kwargs)

        self._msg_var = tk.StringVar(value="◉ SISTEMA LISTO")
        lbl = tk.Label(
            self,
            textvariable=self._msg_var,
            anchor="w",
            font=theme.FONT_MONO_SM,
            bg=theme.BG_DEEP,
            fg=theme.NEON_CYAN,
            padx=theme.PAD_SM,
        )
        lbl.pack(side="left")

        self._count_var = tk.StringVar(value="")
        count_lbl = tk.Label(
            self,
            textvariable=self._count_var,
            anchor="e",
            font=theme.FONT_MONO_SM,
            bg=theme.BG_DEEP,
            fg=theme.TEXT_DIM,
            padx=theme.PAD_SM,
        )
        count_lbl.pack(side="right")

    def info(self, msg: str) -> None:
        self._msg_var.set(f"◉ {msg}")

    def success(self, msg: str) -> None:
        self._msg_var.set(f"✔ {msg}")

    def error(self, msg: str) -> None:
        self._msg_var.set(f"✘ {msg}")

    def warning(self, msg: str) -> None:
        self._msg_var.set(f"⚠ {msg}")

    def set_count(self, n: int) -> None:
        self._count_var.set(f"registros: {n}")


class SectionTitle(tk.Label):
    """Título de sección con prefijo neón."""

    def __init__(self, parent, text: str, **kwargs) -> None:
        super().__init__(
            parent,
            text=theme.neon_title(text),
            font=theme.FONT_MONO_LG,
            fg=theme.NEON_CYAN,
            bg=kwargs.pop("bg", theme.BG_PANEL),
            anchor="w",
            **kwargs,
        )


class ContactoCard(tk.Frame):
    """Tarjeta compacta para mostrar un contacto en la lista."""

    def __init__(self, parent, contacto, **kwargs) -> None:
        super().__init__(parent, bg=theme.BG_CARD, **kwargs)
        c = contacto

        id_lbl = tk.Label(
            self, text=f"#{c.id:>4}", font=theme.FONT_MONO_SM,
            fg=theme.NEON_MAGENTA, bg=theme.BG_CARD, width=6,
        )
        id_lbl.grid(row=0, column=0, rowspan=2, padx=(8, 4), pady=4, sticky="ns")

        name_lbl = tk.Label(
            self, text=c.nombre, font=theme.FONT_MONO_MD,
            fg=theme.TEXT_MAIN, bg=theme.BG_CARD, anchor="w",
        )
        name_lbl.grid(row=0, column=1, sticky="w", padx=4)

        detail_lbl = tk.Label(
            self,
            text=f"{c.telefono}  ·  {c.correo}  ·  {c.ciudad}",
            font=theme.FONT_MONO_SM,
            fg=theme.TEXT_DIM,
            bg=theme.BG_CARD,
            anchor="w",
        )
        detail_lbl.grid(row=1, column=1, sticky="w", padx=4, pady=(0, 4))

        sep = tk.Frame(self, bg=theme.BORDER, height=1)
        sep.grid(row=2, column=0, columnspan=3, sticky="ew")


class ScrollableFrame(tk.Frame):
    """Frame con scrollbar vertical interna."""

    def __init__(self, parent, bg=theme.BG_PANEL, **kwargs) -> None:
        super().__init__(parent, bg=bg, **kwargs)

        canvas = tk.Canvas(self, bg=bg, bd=0, highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        theme.style_scrollbar(sb)

        self.inner = tk.Frame(canvas, bg=bg)
        self.inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)

        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(
            int(-1 * (e.delta / 120)), "units"
        ))


class InfoTextBox(tk.Frame):
    """Text widget de solo lectura estilo consola."""

    def __init__(self, parent, height=10, **kwargs) -> None:
        super().__init__(parent, bg=theme.BG_PANEL, **kwargs)

        self._text = tk.Text(
            self, height=height, state="disabled",
            wrap="word", cursor="arrow",
        )
        theme.style_text(self._text)

        sb = tk.Scrollbar(self, command=self._text.yview)
        theme.style_scrollbar(sb)
        self._text.configure(yscrollcommand=sb.set)

        self._text.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def set_text(self, content: str, color: str = theme.NEON_CYAN) -> None:
        self._text.configure(state="normal")
        self._text.delete("1.0", tk.END)
        self._text.insert(tk.END, content)
        self._text.configure(state="disabled", fg=color)

    def append(self, line: str) -> None:
        self._text.configure(state="normal")
        self._text.insert(tk.END, line + "\n")
        self._text.configure(state="disabled")
        self._text.see(tk.END)
