"""
core/contacto.py
================
Modelo de datos para un Contacto.

Estructura del registro (tamaño fijo = 111 BYTES):
┌─────────┬────────┬────────────────────────────────────────────────────────┐
│ Campo   │ Bytes  │ Descripción                                            │
├─────────┼────────┼────────────────────────────────────────────────────────┤
│ id      │  5     │ ASCII, número entero único, rjust(5) con spaces       │
│ nombre  │ 30     │ ASCII-safe, ljust en bytes hasta 30                    │
│ telefono│ 15     │ ASCII-safe, ljust en bytes hasta 15                    │
│ correo  │ 40     │ ASCII-safe, ljust en bytes hasta 40                    │
│ ciudad  │ 20     │ ASCII-safe, ljust en bytes hasta 20                    │
│ newline │  1     │ b'\\n' separador de registros                           │
├─────────┼────────┼────────────────────────────────────────────────────────┤
│ TOTAL   │ 111    │ bytes por registro                                     │
└─────────┴────────┴────────────────────────────────────────────────────────┘

Nota: Los campos se almacenan en UTF-8 pero se truncan/rellenan a nivel
de BYTES para garantizar RECORD_SIZE exacto. Caracteres multibyte (ej.
acentos en UTF-8) se descomponen si el campo supera su límite en bytes.
"""

from dataclasses import dataclass


# ── Constantes de estructura ──────────────────────────────────────────────────
FIELD_SIZES: dict[str, int] = {
    "id":       5,
    "nombre":   30,
    "telefono": 15,
    "correo":   40,
    "ciudad":   20,
}
RECORD_SIZE: int = sum(FIELD_SIZES.values()) + 1   # +1 por b'\n' = 111


def _encode_field(value: str, size: int) -> bytes:
    """
    Codifica un campo de texto en exactamente `size` bytes UTF-8.
    - Trunca caracteres hasta que quepan en `size` bytes.
    - Rellena con espacios ASCII hasta completar `size` bytes.
    """
    encoded = value.encode("utf-8")
    # Truncar a nivel de bytes (respetando límite multibyte)
    if len(encoded) > size:
        encoded = encoded[:size]
        # Evitar cortar en medio de un carácter multibyte
        while len(encoded) > 0:
            try:
                encoded.decode("utf-8")
                break
            except UnicodeDecodeError:
                encoded = encoded[:-1]
    # Rellenar con espacios hasta `size`
    return encoded + b" " * (size - len(encoded))


def _decode_field(data: bytes) -> str:
    """Decodifica bytes de campo y elimina el relleno de espacios."""
    return data.decode("utf-8", errors="replace").rstrip()


@dataclass
class Contacto:
    """Entidad que representa un contacto en la agenda."""

    id:       int
    nombre:   str
    telefono: str
    correo:   str
    ciudad:   str

    # ── Serialización ─────────────────────────────────────────────────────────

    def to_record(self) -> bytes:
        """
        Serializa el contacto en exactamente RECORD_SIZE bytes.
        Usa _encode_field() que opera a nivel de bytes para garantizar
        el tamaño fijo independientemente de caracteres multibyte UTF-8.
        """
        record = (
            _encode_field(str(self.id).rjust(FIELD_SIZES["id"]), FIELD_SIZES["id"])
            + _encode_field(self.nombre,   FIELD_SIZES["nombre"])
            + _encode_field(self.telefono, FIELD_SIZES["telefono"])
            + _encode_field(self.correo,   FIELD_SIZES["correo"])
            + _encode_field(self.ciudad,   FIELD_SIZES["ciudad"])
            + b"\n"
        )
        assert len(record) == RECORD_SIZE, (
            f"Error interno: registro tiene {len(record)} bytes, "
            f"se esperaban {RECORD_SIZE}"
        )
        return record

    @classmethod
    def from_record(cls, data: bytes) -> "Contacto":
        """
        Deserializa RECORD_SIZE bytes en un Contacto.
        Opera a nivel de bytes para respetar el tamaño fijo.
        Lanza ValueError si el tamaño no coincide.
        """
        if len(data) != RECORD_SIZE:
            raise ValueError(
                f"Tamaño de registro inválido: esperado {RECORD_SIZE}, "
                f"recibido {len(data)}"
            )
        pos = 0

        def _read(size: int) -> str:
            nonlocal pos
            chunk = _decode_field(data[pos : pos + size])
            pos += size
            return chunk

        id_val   = int(_read(FIELD_SIZES["id"]) or "0")
        nombre   = _read(FIELD_SIZES["nombre"])
        telefono = _read(FIELD_SIZES["telefono"])
        correo   = _read(FIELD_SIZES["correo"])
        ciudad   = _read(FIELD_SIZES["ciudad"])
        return cls(id=id_val, nombre=nombre, telefono=telefono,
                   correo=correo, ciudad=ciudad)

    def to_dict(self) -> dict:
        """Devuelve el contacto como diccionario (útil para JSON)."""
        return {
            "id":       self.id,
            "nombre":   self.nombre,
            "telefono": self.telefono,
            "correo":   self.correo,
            "ciudad":   self.ciudad,
        }

    def __str__(self) -> str:
        return (
            f"[{self.id:>5}] {self.nombre:<30} "
            f"Tel: {self.telefono:<15} "
            f"✉  {self.correo:<40} "
            f"📍 {self.ciudad}"
        )
