"""
core/archivo_manager.py
=======================
Manejo de archivos de registros de tamaño fijo.

Implementa acceso aleatorio con seek() y tell(), índice primario en JSON
y verificación de integridad con SHA-256.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Optional

from core.contacto import Contacto, RECORD_SIZE


# ── Rutas por defecto ─────────────────────────────────────────────────────────
DATA_DIR     = Path("data")
DAT_FILE     = DATA_DIR / "contactos.dat"
INDEX_FILE   = DATA_DIR / "indice.json"
HASH_FILE    = DATA_DIR / "contactos.sha256"


class ArchivoManager:
    """
    Gestiona el archivo de registros de tamaño fijo.

    Responsabilidades:
    - Agregar contactos al final del archivo.
    - Leer / modificar un registro directamente por número de posición (seek).
    - Mantener sincronizado el índice id→número_de_registro.
    - Calcular y verificar el hash SHA-256 del archivo de datos.
    """

    def __init__(
        self,
        dat_path:   Path = DAT_FILE,
        index_path: Path = INDEX_FILE,
        hash_path:  Path = HASH_FILE,
    ) -> None:
        self.dat_path   = Path(dat_path)
        self.index_path = Path(index_path)
        self.hash_path  = Path(hash_path)

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_files()

        # Índice en memoria: {str(id): int(numero_registro)}
        self._index: dict[str, int] = self._load_index()

    # ── Inicialización ────────────────────────────────────────────────────────

    def _ensure_files(self) -> None:
        """Crea los archivos necesarios si no existen."""
        if not self.dat_path.exists():
            self.dat_path.touch()
        if not self.index_path.exists():
            self.index_path.write_text("{}", encoding="utf-8")
        if not self.hash_path.exists():
            self.hash_path.write_text("", encoding="utf-8")

    # ── Índice ────────────────────────────────────────────────────────────────

    def _load_index(self) -> dict[str, int]:
        """Carga el índice desde disco."""
        try:
            text = self.index_path.read_text(encoding="utf-8")
            return json.loads(text) if text.strip() else {}
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_index(self) -> None:
        """Persiste el índice en disco."""
        self.index_path.write_text(
            json.dumps(self._index, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def get_index(self) -> dict[str, int]:
        """Devuelve copia del índice en memoria."""
        return dict(self._index)

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def agregar(self, contacto: Contacto) -> int:
        """
        Agrega un contacto al final del archivo.

        Returns:
            Número de registro asignado (0-based).

        Raises:
            ValueError: Si el id ya existe en el índice.
        """
        key = str(contacto.id)
        if key in self._index:
            raise ValueError(f"El id {contacto.id} ya existe.")

        with open(self.dat_path, "ab") as f:
            # tell() muestra la posición ANTES de escribir
            pos_bytes = f.tell()
            num_registro = pos_bytes // RECORD_SIZE
            f.write(contacto.to_record())
            pos_despues = f.tell()  # noqa: F841 – guardamos para trazabilidad

        self._index[key] = num_registro
        self._save_index()
        self._update_hash()
        return num_registro

    def buscar_por_id(self, id_contacto: int) -> Optional[Contacto]:
        """
        Busca un contacto usando el índice primario + seek().

        Returns:
            Contacto si existe, None en caso contrario.
        """
        key = str(id_contacto)
        if key not in self._index:
            return None

        num_registro = self._index[key]
        return self._leer_registro(num_registro)

    def _leer_registro(self, num_registro: int) -> Optional[Contacto]:
        """
        Lee el registro en la posición dada usando seek().

        Args:
            num_registro: Índice 0-based del registro.
        """
        try:
            with open(self.dat_path, "rb") as f:
                offset = num_registro * RECORD_SIZE
                f.seek(offset)                      # ← acceso aleatorio
                pos_actual = f.tell()               # ← verificación con tell()
                assert pos_actual == offset, "seek() no llegó al byte esperado"
                data = f.read(RECORD_SIZE)
            if not data:
                return None
            return Contacto.from_record(data)
        except (OSError, ValueError):
            return None

    def modificar(self, contacto: Contacto) -> bool:
        """
        Sobrescribe in-place el registro del contacto.
        Solo modifica ese registro; el resto del archivo queda intacto.

        Returns:
            True si se modificó, False si el id no existe.
        """
        key = str(contacto.id)
        if key not in self._index:
            return False

        num_registro = self._index[key]
        try:
            with open(self.dat_path, "r+b") as f:
                offset = num_registro * RECORD_SIZE
                f.seek(offset)                      # ← seek directo al registro
                f.write(contacto.to_record())       # ← sobrescritura in-place
        except OSError:
            return False

        self._update_hash()
        return True

    def listar_todos(self) -> list[Contacto]:
        """Lee todos los registros del archivo de forma secuencial."""
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
        """Devuelve el número total de registros en el archivo."""
        size = self.dat_path.stat().st_size if self.dat_path.exists() else 0
        return size // RECORD_SIZE

    def id_existe(self, id_contacto: int) -> bool:
        return str(id_contacto) in self._index

    def proximo_id(self) -> int:
        """Genera el próximo ID disponible."""
        if not self._index:
            return 1
        return max(int(k) for k in self._index) + 1

    # ── Hash / Integridad ─────────────────────────────────────────────────────

    def _calcular_hash(self) -> str:
        """Calcula el SHA-256 del archivo de datos."""
        h = hashlib.sha256()
        try:
            with open(self.dat_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
        except OSError:
            pass
        return h.hexdigest()

    def _update_hash(self) -> None:
        """Recalcula y guarda el hash del archivo."""
        digest = self._calcular_hash()
        self.hash_path.write_text(digest, encoding="utf-8")

    def verificar_integridad(self) -> tuple[bool, str, str]:
        """
        Compara el hash guardado con el hash actual.

        Returns:
            (ok, hash_guardado, hash_actual)
        """
        hash_actual = self._calcular_hash()
        try:
            hash_guardado = self.hash_path.read_text(encoding="utf-8").strip()
        except OSError:
            hash_guardado = ""

        ok = hash_guardado == hash_actual
        return ok, hash_guardado, hash_actual

    def inicializar_hash_si_falta(self) -> None:
        """Si no hay hash guardado, lo calcula y guarda."""
        try:
            guardado = self.hash_path.read_text(encoding="utf-8").strip()
        except OSError:
            guardado = ""
        if not guardado:
            self._update_hash()

    # ── Metadatos ─────────────────────────────────────────────────────────────

    def info_archivo(self) -> dict:
        """Devuelve metadatos del archivo de datos."""
        import datetime
        path = self.dat_path
        if not path.exists():
            return {"existe": False}

        stat = os.stat(path)
        return {
            "existe":           True,
            "ruta":             str(path.resolve()),
            "tamaño_bytes":     stat.st_size,
            "registros":        self.total_registros(),
            "ultima_modificacion": datetime.datetime.fromtimestamp(
                stat.st_mtime
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "lectura":          os.access(path, os.R_OK),
            "escritura":        os.access(path, os.W_OK),
        }
