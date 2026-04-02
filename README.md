# Friolam

Friolam es una **web app con backend SQLite** y UI estilizada con **Tailwind CSS (CDN)**, con vistas separadas por rol:

- Técnico
- Administrador (azul)
- Gerente (morado)

Además incluye API backend:

- `/api/roles`
- `/api/tecnico`
- `/api/administrador`
- `/api/gerente`

## Ejecutar local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
friolam-web
```

Luego abre en el navegador:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/tecnico
- http://127.0.0.1:8000/administrador
- http://127.0.0.1:8000/gerente

Prueba API backend:

```bash
curl http://127.0.0.1:8000/api/roles
```

## Run tests

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Documentación de despliegue

Guía completa de servidor: [docs/SERVER_INSTALL_ES.md](docs/SERVER_INSTALL_ES.md).


> Nota: la UI usa `https://cdn.tailwindcss.com`, por lo que el servidor necesita salida a internet para cargar estilos.
