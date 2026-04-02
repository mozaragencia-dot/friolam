# Friolam

Friolam ahora está preparado como **web app** con vistas separadas por rol:

- Técnico
- Administrador
- Gerente

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

## Run tests

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Documentación de despliegue

Guía completa de servidor: [docs/SERVER_INSTALL_ES.md](docs/SERVER_INSTALL_ES.md).

## FAQ rápida

- **¿Puedo subirlo por FTP?** Sí, preferiblemente SFTP. Revisa la sección FTP en `docs/SERVER_INSTALL_ES.md`.
