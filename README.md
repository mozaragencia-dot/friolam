# Friolam Web App

Sí, ahora está convertida en una **web app completa**.

## Qué puedes hacer

- Capturar información desde formularios web por rol:
  - `/tecnico`
  - `/administrador`
  - `/gerente`
- Ver resumen y datos consolidados en `/dashboard`.
- Guardar todo en base de datos de archivo: `data/friolam_gigante.db`.

## API disponible

- `GET /api/dashboard`
- `GET /api/records?role=tecnico&limit=50&offset=0`
- `POST /api/records`

## Ejecutar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
friolam-web
```

## Pruebas

```bash
python -m unittest discover -s tests -p 'test_*.py'
```
