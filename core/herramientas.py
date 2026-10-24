import zipfile
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.archivo_manager import ArchivoManager


BACKUP_DIR = Path("backups")


class Herramientas:
    """
    Provee operaciones auxiliares sobre los archivos de la agenda.
    """

    def __init__(self, backup_dir: Path = BACKUP_DIR) -> None:
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    # ── Respaldo ──────────────────────────────────────────────────────────────

    def crear_respaldo(self, manager: "ArchivoManager") -> dict:
        """
        Crea un ZIP con contactos.dat + indice.json.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_path  = self.backup_dir / f"respaldo_{timestamp}.zip"

        archivos = [manager.dat_path, manager.index_path]
        tamaño_original = sum(
            p.stat().st_size for p in archivos if p.exists()
        )

        with zipfile.ZipFile(
            zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as zf:
            for p in archivos:
                if p.exists():
                    zf.write(p, arcname=p.name)

        tamaño_zip = zip_path.stat().st_size
        ratio = (
            (1 - tamaño_zip / tamaño_original) * 100
            if tamaño_original > 0 else 0.0
        )

        return {
            "ruta_zip":        zip_path,
            "tamaño_original": tamaño_original,
            "tamaño_zip":      tamaño_zip,
            "ratio":           round(ratio, 2),
        }

    # ── Info de archivo ───────────────────────────────────────────────────────

    def obtener_info_archivo(self, manager: "ArchivoManager") -> dict:
        """
        Devuelve metadatos enriquecidos del archivo de datos.
        Incluye permisos (os.access) y fecha de modificación (os.stat).
        """
        return manager.info_archivo()
