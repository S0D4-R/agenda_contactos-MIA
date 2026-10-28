from dataclasses import dataclass


FIELD_SIZES: dict[str, int] = {
    "id": 5,
    "nombre": 30,
    "telefono": 15,
    "correo": 40,
    "ciudad": 20,
}
RECORD_SIZE: int = sum(FIELD_SIZES.values()) + 1


def _encode_field(value: str, size: int) -> bytes:
    encoded = value.encode("utf-8")
    if len(encoded) > size:
        encoded = encoded[:size]
        while len(encoded) > 0:
            try:
                encoded.decode("utf-8")
                break
            except UnicodeDecodeError:
                encoded = encoded[:-1]
    return encoded + b" " * (size - len(encoded))


def _decode_field(data: bytes) -> str:
    return data.decode("utf-8", errors="replace").rstrip()


@dataclass
class Contacto:
    id: int
    nombre: str
    telefono: str
    correo: str
    ciudad: str

    def to_record(self) -> bytes:
        record = (
            _encode_field(str(self.id).rjust(FIELD_SIZES["id"]), FIELD_SIZES["id"])
            + _encode_field(self.nombre, FIELD_SIZES["nombre"])
            + _encode_field(self.telefono, FIELD_SIZES["telefono"])
            + _encode_field(self.correo, FIELD_SIZES["correo"])
            + _encode_field(self.ciudad, FIELD_SIZES["ciudad"])
            + b"\n"
        )
        assert len(record) == RECORD_SIZE, (
            f"Error interno: registro tiene {len(record)} bytes, "
            f"se esperaban {RECORD_SIZE}"
        )
        return record

    @classmethod
    def from_record(cls, data: bytes) -> "Contacto":
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

        id_val = int(_read(FIELD_SIZES["id"]) or "0")
        nombre = _read(FIELD_SIZES["nombre"])
        telefono = _read(FIELD_SIZES["telefono"])
        correo = _read(FIELD_SIZES["correo"])
        ciudad = _read(FIELD_SIZES["ciudad"])
        return cls(id=id_val, nombre=nombre, telefono=telefono,
                   correo=correo, ciudad=ciudad)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "correo": self.correo,
            "ciudad": self.ciudad,
        }

    def __str__(self) -> str:
        return (
            f"[{self.id:>5}] {self.nombre:<30} "
            f"Tel: {self.telefono:<15} "
            f"✉  {self.correo:<40} "
            f"📍 {self.ciudad}"
        )
