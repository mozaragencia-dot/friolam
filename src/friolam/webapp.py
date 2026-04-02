"""Web app WSGI de Friolam con backend basado en archivo SQLite."""

from __future__ import annotations

import json
from html import escape
from typing import Any
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from friolam.backend import FriolamBackend, default_backend

ROLE_COLORS = {
    "tecnico": "#0f766e",
    "administrador": "#1d4ed8",
    "gerente": "#9333ea",
}


def render_page(title: str, body: str, accent_color: str) -> str:
    return f"""<!doctype html>
<html lang='es'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>{escape(title)}</title>
  <script src='https://cdn.tailwindcss.com'></script>
</head>
<body class='bg-slate-100 text-slate-800'>
  <main class='mx-auto max-w-5xl p-6'>
    <header class='mb-6 rounded-xl border-l-8 bg-white p-5 shadow' style='border-color: {escape(accent_color)}'>
      <h1 class='text-3xl font-bold' style='color: {escape(accent_color)}'>{escape(title)}</h1>
      <p class='mt-2 text-sm'>Base de datos en archivo: <code>data/friolam_gigante.db</code></p>
      <nav class='mt-4 flex flex-wrap gap-2'>
        <a class='rounded bg-slate-200 px-3 py-1' href='/'>Inicio</a>
        <a class='rounded bg-slate-200 px-3 py-1' href='/tecnico'>Técnico</a>
        <a class='rounded bg-slate-200 px-3 py-1' href='/administrador'>Administrador</a>
        <a class='rounded bg-slate-200 px-3 py-1' href='/gerente'>Gerente</a>
      </nav>
    </header>
    <section class='rounded-xl bg-white p-6 shadow'>{body}</section>
  </main>
</body>
</html>"""


def _table_html(records: list[dict[str, Any]]) -> str:
    rows = "".join(
        "<tr class='border-b'>"
        f"<td class='p-2'>{r['id']}</td>"
        f"<td class='p-2'>{escape(str(r['role']))}</td>"
        f"<td class='p-2'>{escape(str(r['nombre']))}</td>"
        f"<td class='p-2'>{escape(str(r['metric_name']))}</td>"
        f"<td class='p-2'>{escape(str(r['metric_value']))}</td>"
        "</tr>"
        for r in records
    )
    return (
        "<div class='overflow-x-auto'><table class='w-full text-sm'>"
        "<thead><tr class='bg-slate-100'><th class='p-2 text-left'>ID</th><th class='p-2 text-left'>Rol</th>"
        "<th class='p-2 text-left'>Nombre</th><th class='p-2 text-left'>Métrica</th><th class='p-2 text-left'>Valor</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div>"
    )


def handle_http(
    method: str,
    path: str,
    query: str,
    body: bytes,
    backend: FriolamBackend | None = None,
) -> tuple[str, str, str]:
    backend = backend or default_backend()

    if method == "POST" and path == "/api/records":
        try:
            payload = json.loads(body.decode("utf-8") or "{}")
            record_id = backend.upsert_record(
                role=str(payload["role"]),
                nombre=str(payload["nombre"]),
                metric_name=str(payload["metric_name"]),
                metric_value=int(payload["metric_value"]),
            )
            return "201 Created", json.dumps({"id": record_id}), "application/json; charset=utf-8"
        except (KeyError, ValueError, json.JSONDecodeError):
            return "400 Bad Request", json.dumps({"error": "payload inválido"}), "application/json; charset=utf-8"

    if method == "GET" and path == "/api/records":
        params = parse_qs(query)
        role = params.get("role", [None])[0]
        limit = int(params.get("limit", ["50"])[0])
        offset = int(params.get("offset", ["0"])[0])
        data = {
            "total": backend.count_records(role=role),
            "items": backend.list_records(role=role, limit=limit, offset=offset),
        }
        return "200 OK", json.dumps(data, ensure_ascii=False), "application/json; charset=utf-8"

    if method == "GET" and path.startswith("/api/records/"):
        try:
            record_id = int(path.split("/api/records/")[-1])
        except ValueError:
            return "400 Bad Request", json.dumps({"error": "id inválido"}), "application/json; charset=utf-8"
        item = backend.get_record(record_id)
        if item is None:
            return "404 Not Found", json.dumps({"error": "no existe"}), "application/json; charset=utf-8"
        return "200 OK", json.dumps(item, ensure_ascii=False), "application/json; charset=utf-8"

    if method == "GET" and path == "/":
        records = backend.list_records(limit=20)
        body_html = (
            "<p class='mb-4'>Plataforma web + backend para alto volumen (paginado por API).</p>"
            "<p class='mb-2'><strong>Endpoints:</strong> GET /api/records, GET /api/records/{id}, POST /api/records</p>"
            + _table_html(records)
        )
        return "200 OK", render_page("Friolam Web Gigante", body_html, accent_color="#334155"), "text/html; charset=utf-8"

    if method == "GET" and path in ["/tecnico", "/administrador", "/gerente"]:
        role = path.strip("/")
        records = backend.list_records(role=role, limit=50)
        body_html = f"<h2 class='mb-4 text-xl font-semibold'>Vista {escape(role.title())}</h2>" + _table_html(records)
        return "200 OK", render_page(f"Vista {role.title()}", body_html, accent_color=ROLE_COLORS[role]), "text/html; charset=utf-8"

    return "404 Not Found", render_page("No encontrado", "<p>Ruta no válida.</p>", accent_color="#dc2626"), "text/html; charset=utf-8"


def app(environ: dict, start_response, backend: FriolamBackend | None = None) -> list[bytes]:
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "/")
    query = environ.get("QUERY_STRING", "")
    length = int(environ.get("CONTENT_LENGTH") or 0)
    body = environ["wsgi.input"].read(length) if length else b""

    status, content, content_type = handle_http(method, path, query, body, backend=backend)
    start_response(status, [("Content-Type", content_type)])
    return [content.encode("utf-8")]


def main() -> None:
    host, port = "0.0.0.0", 8000
    backend = default_backend()
    print(f"Friolam web gigante en http://{host}:{port} usando {backend.db_file}")
    with make_server(host, port, lambda e, s: app(e, s, backend=backend)) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
