# Friolam

Friolam fue reescrito como **web app completa** con backend de alto volumen basado en archivo SQLite.

## Base de datos de archivo (gigante)

La aplicación usa el archivo:

- `data/friolam_gigante.db`

Esta base está optimizada para volumen con:

- `WAL` para concurrencia de lectura/escritura.
- índices por `role` y `nombre`.
- endpoints con paginación (`limit`/`offset`).

## Ejecutar local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
friolam-web
```

## Web y API

Web:
- `/`
- `/tecnico`
- `/administrador`
- `/gerente`

API:
- `GET /api/records?role=tecnico&limit=50&offset=0`
- `GET /api/records/{id}`
- `POST /api/records`

Ejemplo POST:

```bash
curl -X POST http://127.0.0.1:8000/api/records \
  -H 'Content-Type: application/json' \
  -d '{"role":"gerente","nombre":"Carla","metric_name":"objetivos_trimestrales","metric_value":15}'
```

## Pruebas

```bash
python -m unittest discover -s tests -p 'test_*.py'
```
