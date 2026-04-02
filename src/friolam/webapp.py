"""Aplicación web minimalista (WSGI) para Friolam."""

from __future__ import annotations

import json
from html import escape
from wsgiref.simple_server import make_server

from friolam.backend import FriolamBackend, default_backend


def render_page(title: str, body: str, accent_color: str = "#2563eb") -> str:
    """Render HTML page styled with Tailwind CSS."""
    return f"""<!doctype html>
<html lang='es'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>{escape(title)}</title>
  <script src='https://cdn.tailwindcss.com'></script>
</head>
<body class='bg-slate-100 text-slate-800'>
  <main class='mx-auto max-w-4xl p-6'>
    <header class='mb-6 rounded-xl border-l-8 bg-white p-5 shadow' style='border-color: {escape(accent_color)}'>
      <h1 class='text-3xl font-bold' style='color: {escape(accent_color)}'>{escape(title)}</h1>
      <nav class='mt-3 flex flex-wrap gap-3 text-sm font-semibold'>
        <a class='rounded bg-slate-100 px-3 py-1 hover:bg-slate-200' href='/'>Inicio</a>
        <a class='rounded bg-slate-100 px-3 py-1 hover:bg-slate-200' href='/tecnico'>Técnico</a>
        <a class='rounded bg-slate-100 px-3 py-1 hover:bg-slate-200' href='/administrador'>Administrador</a>
        <a class='rounded bg-slate-100 px-3 py-1 hover:bg-slate-200' href='/gerente'>Gerente</a>
      </nav>
    </header>
    <section class='rounded-xl bg-white p-6 shadow'>
      {body}
    </section>
  </main>
</body>
</html>"""


def _role_html(role_data: dict[str, str | int], title: str) -> str:
    return (
        f"<h2 class='mb-4 text-2xl font-semibold'>{escape(title)}</h2>"
        f"<p class='mb-2'><strong>Nombre:</strong> {escape(str(role_data['nombre']))}</p>"
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
            "<p class='mb-3'>Panel principal de Friolam con backend SQLite.</p>"
            "<ul class='list-disc space-y-1 pl-6'>"
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
