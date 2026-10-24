# Agenda de Contactos con Acceso Aleatorio
**Laboratorio No. 2 — Manejo de Archivos**  
Universidad Rafael Landívar — Campus Quetzaltenango  
Ingeniería en Informática y Sistemas — Octubre 2026

---

## Estructura del proyecto

```
agenda_contactos/
├── main.py                        ← Punto de entrada
├── requirements.txt
├── core/
│   ├── contacto.py                ← Modelo Contacto + RECORD_SIZE
│   ├── archivo_manager.py         ← seek/tell, índice, hash SHA-256
│   ├── exportador.py              ← JSON + PDF (fpdf2)
│   └── herramientas.py            ← ZIP respaldo + metadatos
├── ui/
│   ├── theme.py                   ← Tokens de diseño cyberpunk
│   ├── widgets.py                 ← Componentes Tkinter reutilizables
│   ├── app.py                     ← Ventana principal + dashboard
│   ├── ventana_contactos.py       ← Agregar / buscar / modificar
│   ├── ventana_exportar.py        ← Exportar JSON y PDF
│   ├── ventana_herramientas.py    ← Integridad, ZIP, info archivo
│   └── ventana_ayuda.py           ← Manual de usuario (simulado)
├── utils/
│   └── test_sistema.py            ← Suite de pruebas funcionales
├── data/                          ← Generado en ejecución
│   ├── contactos.dat
│   ├── indice.json
│   └── contactos.sha256
├── exports/                       ← Generado en ejecución
└── backups/                       ← Generado en ejecución
```

---

## Estructura del registro (tamaño fijo = 111 bytes)

| Campo    | Bytes | Método de relleno | Descripción             |
|----------|------:|-------------------|-------------------------|
| id       |     5 | `rjust(5)`        | Entero único, a derecha |
| nombre   |    30 | `ljust(30)`       | Texto, a la izquierda   |
| telefono |    15 | `ljust(15)`       | Texto, a la izquierda   |
| correo   |    40 | `ljust(40)`       | Texto, a la izquierda   |
| ciudad   |    20 | `ljust(20)`       | Texto, a la izquierda   |
| `\n`     |     1 | separador         | Nueva línea             |
| **TOTAL**| **111** |                 |                         |

---

## Acceso aleatorio — seek() y tell()

```python
# Leer registro N directamente:
offset = N * RECORD_SIZE          # ej. N=2 → offset=222
f.seek(offset)                    # posiciona el cursor
pos = f.tell()                    # verifica posición
data = f.read(RECORD_SIZE)        # lee exactamente 111 bytes

# Modificar in-place (solo sobreescribe ese registro):
with open(dat_path, "r+b") as f:
    f.seek(num_registro * RECORD_SIZE)
    f.write(contacto.to_record())  # los demás registros intactos
```

---

## Índice primario

```json
{
  "1": 0,
  "2": 1,
  "3": 2
}
```

Búsqueda O(1) vs. O(n) secuencial:
1. Consultar `indice.json` → obtener `num_registro`
2. `seek(num_registro × RECORD_SIZE)` → leer directamente

---

## Instalación y ejecución

```bash
# Instalar dependencias
pip install fpdf2

# Ejecutar aplicación
python main.py

# Ejecutar pruebas
python utils/test_sistema.py
```

---

## Archivos generados

| Archivo              | Descripción                        |
|----------------------|------------------------------------|
| `data/contactos.dat`   | Registros de tamaño fijo (111 B)   |
| `data/indice.json`     | Índice id → número de registro     |
| `data/contactos.sha256`| Hash SHA-256 para integridad       |
| `exports/*.json`       | Exportación completa de contactos  |
| `exports/*.pdf`        | Reporte PDF con diseño cyberpunk   |
| `backups/*.zip`        | Respaldo comprimido (dat + índice) |
