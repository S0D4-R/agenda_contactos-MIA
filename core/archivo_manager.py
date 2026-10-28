import hashlib
import json
import os
from pathlib import Path
from typing import Optional

from core.contacto import Contacto, RECORD_SIZE


DATA_DIR = Path("data")
DAT_FILE = DATA_DIR / "contactos.dat"
INDEX_FILE = DATA_DIR / "indice.json"
HASH_FILE = DATA_DIR / "contactos.sha256"


class ArchivoManager:
    def __init__(
        self,
        dat_path: Path = DAT_FILE,
        index_path: Path = INDEX_FILE,
        hash_path: Path = HASH_FILE,
    ) -> None:
        self.dat_path = Path(dat_path)
        self.index_path = Path(index_path)
        self.hash_path = Path(hash_path)

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_files()
        self._index: dict[str, int] = self._load_index()

    def _ensure_files(self) -> None:
        if not self.dat_path.exists():
            self.dat_path.touch()
        if not self.index_path.exists():
            self.index_path.write_text("{}", encoding="utf-8")
        if not self.hash_path.exists():
            self.hash_path.write_text("", encoding="utf-8")

    def _load_index(self) -> dict[str, int]:
        try:
            text = self.index_path.read_text(encoding="utf-8")
            return json.loads(text) if text.strip() else {}
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_index(self) -> None:
        self.index_path.write_text(
            json.dumps(self._index, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def get_index(self) -> dict[str, int]:
        return dict(self._index)

    def agregar(self, contacto: Contacto) -> int:
        key = str(contacto.id)
        if key in self._index:
            raise ValueError(f"El id {contacto.id} ya existe.")

        with open(self.dat_path, "ab") as f:
            pos_bytes = f.tell()
            num_registro = pos_bytes // RECORD_SIZE
            f.write(contacto.to_record())

        self._index[key] = num_registro
        self._save_index()
        self._update_hash()
        return num_registro

    def buscar_por_id(self, id_contacto: int) -> Optional[Contacto]:
        key = str(id_contacto)
        if key not in self._index:
            return None

        num_registro = self._index[key]
        return self._leer_registro(num_registro)

    def _leer_registro(self, num_registro: int) -> Optional[Contacto]:
        try:
            with open(self.dat_path, "rb") as f:
                offset = num_registro * RECORD_SIZE
                f.seek(offset)
                pos_actual = f.tell()
                assert pos_actual == offset, "seek() no llegó al byte esperado"
                data = f.read(RECORD_SIZE)
            if not data:
                return None
            return Contacto.from_record(data)
        except (OSError, ValueError):
            return None

    def modificar(self, contacto: Contacto) -> bool:
        key = str(contacto.id)
        if key not in self._index:
            return False

        num_registro = self._index[key]
        try:
            with open(self.dat_path, "r+b") as f:
                offset = num_registro * RECORD_SIZE
                f.seek(offset)
                f.write(contacto.to_record())
        except OSError:
            return False

        self._update_hash()
        return True

    def listar_todos(self) -> list[Contacto]:
        contactos: list[Contacto] = []
        if not self.dat_path.exists():
            return contactos

        with open(self.dat_path, "rb") as f:
            while True:
                data = f.read(RECORD_SIZE)
                if not data:
                    break
                try:
                    contactos.append(Contacto.from_record(data))
                except ValueError:
                    continue
        return contactos

    def total_registros(self) -> int:
        size = self.dat_path.stat().st_size if self.dat_path.exists() else 0
        return size // RECORD_SIZE

    def id_existe(self, id_contacto: int) -> bool:
        return str(id_contacto) in self._index

    def proximo_id(self) -> int:
        if not self._index:
            return 1
        return max(int(k) for k in self._index) + 1

    def _calcular_hash(self) -> str:
        h = hashlib.sha256()
        try:
            with open(self.dat_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
        except OSError:
            pass
        return h.hexdigest()

    def _update_hash(self) -> None:
        digest = self._calcular_hash()
        self.hash_path.write_text(digest, encoding="utf-8")

    def verificar_integridad(self) -> tuple[bool, str, str]:
        hash_actual = self._calcular_hash()
        try:
            hash_guardado = self.hash_path.read_text(encoding="utf-8").strip()
        except OSError:
            hash_guardado = ""

        ok = hash_guardado == hash_actual
        return ok, hash_guardado, hash_actual

    def inicializar_hash_si_falta(self) -> None:
        try:
            guardado = self.hash_path.read_text(encoding="utf-8").strip()
        except OSError:
            guardado = ""
        if not guardado:
            self._update_hash()

    def info_archivo(self) -> dict:
        import datetime
        path = self.dat_path
        if not path.exists():
            return {"existe": False}

        stat = os.stat(path)
        return {
            "existe": True,
            "ruta": str(path.resolve()),
            "tamaño_bytes": stat.st_size,
            "registros": self.total_registros(),
            "ultima_modificacion": datetime.datetime.fromtimestamp(
                stat.st_mtime
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "lectura": os.access(path, os.R_OK),
            "escritura": os.access(path, os.W_OK),
        }
