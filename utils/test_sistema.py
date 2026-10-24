"""
utils/test_sistema.py
=====================
Suite de pruebas funcionales para todos los módulos del sistema.
Ejecutar desde la raíz del proyecto: python utils/test_sistema.py
"""

import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import json
import shutil
import tempfile
from pathlib import Path


# ── Colores de consola ────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

passed = 0
failed = 0


def ok(msg: str) -> None:
    global passed
    passed += 1
    print(f"  {GREEN}✔{RESET}  {msg}")


def fail(msg: str, err: str = "") -> None:
    global failed
    failed += 1
    print(f"  {RED}✘{RESET}  {msg}")
    if err:
        print(f"      {RED}→ {err}{RESET}")


def section(title: str) -> None:
    print(f"\n{CYAN}{BOLD}{'─'*55}{RESET}")
    print(f"{CYAN}{BOLD}  {title}{RESET}")
    print(f"{CYAN}{'─'*55}{RESET}")


# ── Directorio temporal aislado ───────────────────────────────────────────────
TMP_DIR = Path(tempfile.mkdtemp(prefix="agenda_test_"))


def make_manager():
    from core.archivo_manager import ArchivoManager
    return ArchivoManager(
        dat_path   = TMP_DIR / "contactos.dat",
        index_path = TMP_DIR / "indice.json",
        hash_path  = TMP_DIR / "contactos.sha256",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 1. Modelo Contacto
# ─────────────────────────────────────────────────────────────────────────────
section("1. MODELO Contacto (core/contacto.py)")

try:
    from core.contacto import Contacto, RECORD_SIZE, FIELD_SIZES

    c = Contacto(1, "Ana García", "55551234", "ana@mail.com", "Guatemala")
    record = c.to_record()

    if len(record) == RECORD_SIZE:
        ok(f"to_record() produce {RECORD_SIZE} bytes exactos")
    else:
        fail(f"to_record() tamaño incorrecto: {len(record)} ≠ {RECORD_SIZE}")

    c2 = Contacto.from_record(record)
    if c2.id == 1 and c2.nombre == "Ana García" and c2.ciudad == "Guatemala":
        ok("from_record() deserializa correctamente")
    else:
        fail("from_record() datos incorrectos", str(c2))

    d = c.to_dict()
    if all(k in d for k in ["id","nombre","telefono","correo","ciudad"]):
        ok("to_dict() incluye todos los campos requeridos")
    else:
        fail("to_dict() faltan campos")

    total = sum(FIELD_SIZES.values()) + 1
    if total == RECORD_SIZE:
        ok(f"RECORD_SIZE documentado correctamente: {RECORD_SIZE} bytes")
    else:
        fail(f"RECORD_SIZE inconsistente: {total} ≠ {RECORD_SIZE}")

except Exception as e:
    fail("Error en módulo Contacto", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 2. ArchivoManager — Agregar y seek/tell
# ─────────────────────────────────────────────────────────────────────────────
section("2. ARCHIVO MANAGER — seek() / tell() / índice")

try:
    from core.contacto import Contacto, RECORD_SIZE
    mgr = make_manager()

    c1 = Contacto(101, "Luis Morales", "55550001", "luis@x.com", "Quetzaltenango")
    c2 = Contacto(102, "María López",  "55550002", "maria@x.com","Huehuetenango")
    c3 = Contacto(103, "Pedro Pérez",  "55550003", "pedro@x.com","Xela")

    n1 = mgr.agregar(c1)
    n2 = mgr.agregar(c2)
    n3 = mgr.agregar(c3)

    if n1 == 0 and n2 == 1 and n3 == 2:
        ok("Números de registro asignados correctamente (0-based)")
    else:
        fail(f"Números de registro incorrectos: {n1},{n2},{n3}")

    # Verificar tamaño del archivo
    size = (TMP_DIR / "contactos.dat").stat().st_size
    if size == 3 * RECORD_SIZE:
        ok(f"Archivo tiene tamaño exacto: {size} bytes = 3 × {RECORD_SIZE}")
    else:
        fail(f"Tamaño de archivo incorrecto: {size}")

    # Verificar seek directo
    with open(TMP_DIR / "contactos.dat", "rb") as f:
        f.seek(1 * RECORD_SIZE)
        pos = f.tell()
        if pos == RECORD_SIZE:
            ok(f"seek(1 × RECORD_SIZE) → tell() = {pos} ✔")
        else:
            fail(f"tell() incorrecto: {pos}")

    # Índice
    idx = mgr.get_index()
    if "101" in idx and "102" in idx and "103" in idx:
        ok("Índice contiene los 3 IDs registrados")
    else:
        fail("Índice incompleto", str(idx))

    if idx["102"] == 1:
        ok("Índice mapea correctamente ID→número_de_registro")
    else:
        fail(f"Índice mapa incorrecto: índice['102']={idx.get('102')}")

except Exception as e:
    fail("Error en ArchivoManager agregar", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 3. Búsqueda por ID (índice + seek)
# ─────────────────────────────────────────────────────────────────────────────
section("3. BÚSQUEDA POR ID (índice primario + seek directo)")

try:
    mgr = make_manager()
    mgr.agregar(Contacto(201, "Sofía Ruiz", "55550010", "sofia@x.com", "Ciudad de Guatemala"))
    mgr.agregar(Contacto(202, "Carlos Vega","55550020", "carlos@x.com","Antigua"))

    found = mgr.buscar_por_id(202)
    if found and found.nombre == "Carlos Vega":
        ok("buscar_por_id(202) devuelve el contacto correcto")
    else:
        fail("buscar_por_id no encontró el contacto correcto")

    not_found = mgr.buscar_por_id(999)
    if not_found is None:
        ok("buscar_por_id devuelve None para ID inexistente")
    else:
        fail("buscar_por_id no devuelve None para ID inexistente")

except Exception as e:
    fail("Error en búsqueda por ID", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 4. Modificación in-place
# ─────────────────────────────────────────────────────────────────────────────
section("4. MODIFICACIÓN IN-PLACE (seek + sobrescritura)")

try:
    mgr = make_manager()
    mgr.agregar(Contacto(301, "Original Nombre","55550000","orig@x.com","CiudadA"))
    mgr.agregar(Contacto(302, "Otro Contacto",  "55550001","otro@x.com","CiudadB"))

    size_antes = (TMP_DIR / "contactos.dat").stat().st_size

    modificado = Contacto(301, "Nombre Cambiado","55559999","new@x.com","CiudadX")
    ok_mod = mgr.modificar(modificado)

    size_despues = (TMP_DIR / "contactos.dat").stat().st_size

    if ok_mod:
        ok("modificar() retorna True para ID existente")
    else:
        fail("modificar() retornó False inesperadamente")

    if size_antes == size_despues:
        ok("El archivo NO cambió de tamaño (modificación in-place)")
    else:
        fail(f"El archivo cambió de tamaño: {size_antes}→{size_despues}")

    leido = mgr.buscar_por_id(301)
    if leido and leido.nombre == "Nombre Cambiado":
        ok("El dato modificado se lee correctamente después del seek")
    else:
        fail("El dato modificado no se leyó correctamente")

    intacto = mgr.buscar_por_id(302)
    if intacto and intacto.nombre == "Otro Contacto":
        ok("El registro adyacente NO fue afectado por la modificación")
    else:
        fail("El registro adyacente fue alterado")

except Exception as e:
    fail("Error en modificación in-place", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 5. Hash SHA-256 / Integridad
# ─────────────────────────────────────────────────────────────────────────────
section("5. INTEGRIDAD SHA-256 (hashlib)")

try:
    mgr = make_manager()
    mgr.agregar(Contacto(401, "Hash Test","55550000","hash@x.com","TestCity"))

    ok1, h_guard, h_act = mgr.verificar_integridad()
    if ok1:
        ok("Integridad OK después de agregar contacto")
    else:
        fail("Integridad falló sin modificación externa")

    # Corromper el archivo manualmente
    dat = TMP_DIR / "contactos.dat"
    content = dat.read_bytes()
    dat.write_bytes(content + b"CORRUPT")

    ok2, h_guard2, h_act2 = mgr.verificar_integridad()
    if not ok2:
        ok("Integridad detecta modificación externa ✔")
    else:
        fail("Integridad NO detectó la modificación externa")

    if h_guard2 != h_act2:
        ok("Hashes difieren correctamente tras corrupción")
    else:
        fail("Hashes deberían diferir")

except Exception as e:
    fail("Error en verificación de integridad", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 6. Exportación JSON
# ─────────────────────────────────────────────────────────────────────────────
section("6. EXPORTACIÓN JSON (core/exportador.py)")

try:
    mgr = make_manager()
    mgr.agregar(Contacto(501, "Export Test1","55550001","e1@x.com","Ciudad1"))
    mgr.agregar(Contacto(502, "Export Test2","55550002","e2@x.com","Ciudad2"))

    from core.exportador import Exportador
    exp = Exportador(export_dir=TMP_DIR / "exports")
    contactos = mgr.listar_todos()
    ruta_json = exp.exportar_json(contactos)

    if ruta_json.exists():
        ok(f"Archivo JSON creado: {ruta_json.name}")
    else:
        fail("Archivo JSON no fue creado")

    data = json.loads(ruta_json.read_text(encoding="utf-8"))
    if data["total"] == len(contactos):
        ok(f"JSON contiene {data['total']} registros correctos")
    else:
        fail(f"JSON total={data['total']} ≠ {len(contactos)}")

    if "generado_en" in data:
        ok("JSON incluye timestamp de generación")
    else:
        fail("JSON no incluye timestamp")

except Exception as e:
    fail("Error en exportación JSON", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 7. Exportación PDF
# ─────────────────────────────────────────────────────────────────────────────
section("7. EXPORTACIÓN PDF (fpdf2)")

try:
    from core.exportador import Exportador
    from core.contacto import Contacto

    exp = Exportador(export_dir=TMP_DIR / "exports")
    contactos = [
        Contacto(601, "PDF Test 1","55550001","p1@x.com","Ciudad1"),
        Contacto(602, "PDF Test 2","55550002","p2@x.com","Ciudad2"),
    ]
    ruta_pdf = exp.exportar_pdf(contactos)

    if ruta_pdf.exists() and ruta_pdf.stat().st_size > 0:
        ok(f"PDF creado: {ruta_pdf.name} ({ruta_pdf.stat().st_size:,} bytes)")
    else:
        fail("PDF no fue creado o está vacío")

    # Verificar header PDF
    magic = ruta_pdf.read_bytes()[:4]
    if magic == b"%PDF":
        ok("Archivo comienza con magic bytes %PDF ✔")
    else:
        fail(f"Magic bytes incorrectos: {magic}")

except Exception as e:
    fail("Error en exportación PDF", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 8. Respaldo ZIP
# ─────────────────────────────────────────────────────────────────────────────
section("8. RESPALDO ZIP (zipfile)")

try:
    import zipfile as zf
    mgr = make_manager()
    mgr.agregar(Contacto(701, "ZIP Test","55550001","zip@x.com","ZipCity"))

    from core.herramientas import Herramientas
    herr = Herramientas(backup_dir=TMP_DIR / "backups")
    res  = herr.crear_respaldo(mgr)

    if res["ruta_zip"].exists():
        ok(f"ZIP creado: {res['ruta_zip'].name}")
    else:
        fail("ZIP no fue creado")

    if zf.is_zipfile(res["ruta_zip"]):
        ok("Archivo es un ZIP válido")
    else:
        fail("Archivo ZIP inválido")

    if res["tamaño_original"] > 0 and res["tamaño_zip"] > 0:
        ok(f"Tamaños: orig={res['tamaño_original']}B → zip={res['tamaño_zip']}B "
           f"({res['ratio']:.1f}% reducción)")
    else:
        fail("Tamaños de archivo inválidos")

    with zf.ZipFile(res["ruta_zip"]) as z:
        names = z.namelist()
    if "contactos.dat" in names:
        ok("ZIP contiene contactos.dat")
    else:
        fail("ZIP no contiene contactos.dat")

    if "indice.json" in names:
        ok("ZIP contiene indice.json")
    else:
        fail("ZIP no contiene indice.json")

except Exception as e:
    fail("Error en respaldo ZIP", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 9. Metadatos y permisos
# ─────────────────────────────────────────────────────────────────────────────
section("9. METADATOS Y PERMISOS (os.stat / os.access)")

try:
    from core.herramientas import Herramientas
    mgr  = make_manager()
    mgr.agregar(Contacto(801, "Meta Test","55550001","meta@x.com","MetaCity"))
    herr = Herramientas()
    info = herr.obtener_info_archivo(mgr)

    required = ["existe","ruta","tamaño_bytes","registros",
                "ultima_modificacion","lectura","escritura"]
    missing  = [k for k in required if k not in info]

    if not missing:
        ok("info_archivo() devuelve todos los campos requeridos")
    else:
        fail(f"Faltan campos: {missing}")

    if info["existe"]:
        ok(f"tamaño_bytes = {info['tamaño_bytes']:,}")
        ok(f"ultima_modificacion = {info['ultima_modificacion']}")
        ok(f"lectura={info['lectura']}  escritura={info['escritura']}")
    else:
        fail("info_archivo dice que el archivo no existe")

except Exception as e:
    fail("Error en metadatos", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 10. Manejo de errores
# ─────────────────────────────────────────────────────────────────────────────
section("10. MANEJO DE ERRORES")

try:
    mgr = make_manager()

    # ID duplicado
    mgr.agregar(Contacto(901, "Error Test","55550001","err@x.com","ErrCity"))
    try:
        mgr.agregar(Contacto(901, "Duplicado","55550002","dup@x.com","DupCity"))
        fail("Debería haber lanzado ValueError por ID duplicado")
    except ValueError:
        ok("ValueError lanzado correctamente para ID duplicado")

    # Buscar ID inexistente
    res = mgr.buscar_por_id(99999)
    if res is None:
        ok("buscar_por_id retorna None para ID inexistente (no crash)")
    else:
        fail("buscar_por_id no retornó None")

    # Modificar ID inexistente
    c_inexistente = Contacto(99999, "Inexistente","0","x@x.com","X")
    result = mgr.modificar(c_inexistente)
    if result is False:
        ok("modificar() retorna False para ID inexistente (no crash)")
    else:
        fail("modificar() no retornó False para ID inexistente")

    # Archivo index corrupto
    idx_path = TMP_DIR / "indice_corrupt.json"
    idx_path.write_text("{ INVALID JSON }", encoding="utf-8")
    from core.archivo_manager import ArchivoManager
    mgr2 = ArchivoManager(
        dat_path   = TMP_DIR / "contactos_c.dat",
        index_path = idx_path,
        hash_path  = TMP_DIR / "hash_c.sha256",
    )
    if isinstance(mgr2.get_index(), dict):
        ok("Índice corrupto → carga como dict vacío sin crash")
    else:
        fail("Índice corrupto causó error inesperado")

except Exception as e:
    fail("Error inesperado en manejo de errores", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Resumen
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{CYAN}{'═'*55}{RESET}")
total = passed + failed
pct   = (passed / total * 100) if total else 0
color = GREEN if failed == 0 else (YELLOW if failed < 3 else RED)
print(
    f"{color}{BOLD}  RESULTADO: {passed}/{total} pruebas pasadas ({pct:.0f}%){RESET}"
)
if failed == 0:
    print(f"{GREEN}{BOLD}  ✔  TODOS LOS MÓDULOS FUNCIONAN CORRECTAMENTE{RESET}")
else:
    print(f"{RED}{BOLD}  ✘  {failed} PRUEBA(S) FALLARON — revisar arriba{RESET}")
print(f"{CYAN}{'═'*55}{RESET}\n")

# Limpiar directorio temporal
shutil.rmtree(TMP_DIR, ignore_errors=True)

sys.exit(0 if failed == 0 else 1)
