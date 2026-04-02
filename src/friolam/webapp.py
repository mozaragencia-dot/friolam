"""Aplicación web minimalista (WSGI) para Friolam."""

from __future__ import annotations

import json
from html import escape
from wsgiref.simple_server import make_server

from friolam.backend import FriolamBackend, default_backend


def render_page(title: str, body: str, accent_color: str = "#2563eb") -> str:
    """Render basic HTML page."""
    return f"""<!doctype html>
<html lang='es'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>{escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    .card {{ border: 2px solid {escape(accent_color)}; border-radius: 8px; padding: 1rem; max-width: 800px; }}
    h1 {{ color: {escape(accent_color)}; }}
    nav a {{ margin-right: 1rem; color: {escape(accent_color)}; }}
  </style>
</head>
<body>
  <h1>{escape(title)}</h1>
  <nav>
    <a href='/'>Inicio</a>
    <a href='/tecnico'>Técnico</a>
    <a href='/administrador'>Administrador</a>
    <a href='/gerente'>Gerente</a>
  </nav>
  <div class='card'>{body}</div>
</body>
</html>"""


def _role_html(role_data: dict[str, str | int], title: str) -> str:
    return (
        f"<h2>{escape(title)}</h2>"
        f"<p><strong>Nombre:</strong> {escape(str(role_data['nombre']))}</p>"
        f"<p><strong>{escape(str(role_data['detalle_1']))}:</strong> {escape(str(role_data['detalle_2']))}</p>"
    )


def handle_path(path: str, backend: FriolamBackend | None = None) -> tuple[str, str, str]:
    """Resolve URL path into status, content and content type."""
    backend = backend or default_backend()

    if path == "/api/roles":
        return "200 OK", json.dumps(backend.get_all_roles(), ensure_ascii=False), "application/json; charset=utf-8"

    if path.startswith("/api/"):
        role = path.split("/api/")[-1]
        try:
            payload = backend.get_role(role)
            return "200 OK", json.dumps(payload, ensure_ascii=False), "application/json; charset=utf-8"
        except KeyError:
            return "404 Not Found", json.dumps({"error": "role not found"}), "application/json; charset=utf-8"

    if path == "/":
        body = (
            "<p>Panel principal de Friolam con backend SQLite.</p>"
            "<ul>"
            "<li><strong>Técnico:</strong> vista operativa.</li>"
            "<li><strong>Administrador:</strong> estado de plataforma.</li>"
            "<li><strong>Gerente:</strong> seguimiento estratégico.</li>"
            "<li><strong>API:</strong> /api/roles, /api/tecnico, /api/administrador, /api/gerente.</li>"
            "</ul>"
        )
        return "200 OK", render_page("Friolam Web App", body, accent_color="#334155"), "text/html; charset=utf-8"

    role_config = {
        "/tecnico": ("tecnico", "Vista Técnico", "Modelo Técnico", "#0f766e"),
        "/administrador": ("administrador", "Vista Administrador", "Modelo Administrador", "#1d4ed8"),
        "/gerente": ("gerente", "Vista Gerente", "Modelo Gerente", "#9333ea"),
    }

    if path in role_config:
        role_key, page_title, card_title, color = role_config[path]
        data = backend.get_role(role_key)
        body = _role_html(data, card_title)
        return "200 OK", render_page(page_title, body, accent_color=color), "text/html; charset=utf-8"

    return "404 Not Found", render_page("No encontrado", "<p>Ruta no válida.</p>", accent_color="#dc2626"), "text/html; charset=utf-8"


def app(environ: dict, start_response, backend: FriolamBackend | None = None) -> list[bytes]:
    """WSGI entrypoint."""
    path = environ.get("PATH_INFO", "/")
    status, content, content_type = handle_path(path, backend=backend)
    headers = [("Content-Type", content_type)]
    start_response(status, headers)
    return [content.encode("utf-8")]


def main() -> None:
    """Run the web app server."""
    host = "0.0.0.0"
    port = 8000
    backend = default_backend()
    print(f"Friolam web app + backend escuchando en http://{host}:{port}")
    with make_server(host, port, lambda e, s: app(e, s, backend=backend)) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
