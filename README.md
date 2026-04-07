# Friolam

Ahora Friolam incluye una versión web funcional para captura y dashboard usando **Ionic (CDN)** + backend SQLite en archivo.

## ¿Qué ya funciona?

- Los técnicos (y otros roles) pueden ingresar información desde `/ionic`.
- Esa información se guarda en el archivo `data/friolam_gigante.db`.
- El dashboard muestra resumen por rol y últimos registros.

## Rutas principales

UI:
- `/` (resumen)
- `/ionic` (formulario + dashboard en Ionic)
- `/tecnico`
- `/administrador`
- `/gerente`

API:
- `GET /api/dashboard`
- `GET /api/records?role=tecnico&limit=50&offset=0`
- `GET /api/records/{id}`
- `POST /api/records`

## Ejecutar local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
friolam-web
```

## Ejemplo de carga por API

```bash
curl -X POST http://127.0.0.1:8000/api/records \
  -H 'Content-Type: application/json' \
  -d '{"role":"tecnico","nombre":"Juan","metric_name":"tickets_abiertos","metric_value":8}'
```

## Pruebas

```bash
python -m unittest discover -s tests -p 'test_*.py'
```
