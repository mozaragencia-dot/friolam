"""Web app WSGI de Friolam con formularios y dashboard."""

from __future__ import annotations

import json
from html import escape
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from friolam.backend import FriolamBackend, default_backend

ROLE_COLORS = {
    "tecnico": "#0f766e",
    "administrador": "#1d4ed8",
    "gerente": "#9333ea",
}


NAV = """
<nav class='mt-4 flex flex-wrap gap-2'>
  <a class='rounded bg-slate-200 px-3 py-1' href='/'>Inicio</a>
  <a class='rounded bg-slate-200 px-3 py-1' href='/dashboard'>Dashboard</a>
  <a class='rounded bg-slate-200 px-3 py-1' href='/tecnico'>Técnico</a>
  <a class='rounded bg-slate-200 px-3 py-1' href='/administrador'>Administrador</a>
  <a class='rounded bg-slate-200 px-3 py-1' href='/gerente'>Gerente</a>
</nav>
"""


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
      <p class='mt-2 text-sm'>Base de datos: <code>data/friolam_gigante.db</code></p>
      {NAV}
    </header>
    <section class='rounded-xl bg-white p-6 shadow'>{body}</section>
  </main>
</body>
</html>"""


def _table(records: list[dict]) -> str:
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
        "<table class='w-full text-sm'>"
        "<thead><tr class='bg-slate-100'><th class='p-2 text-left'>ID</th><th class='p-2 text-left'>Rol</th><th class='p-2 text-left'>Nombre</th><th class='p-2 text-left'>Métrica</th><th class='p-2 text-left'>Valor</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


def _capture_form(role: str) -> str:
    default_metric = {
        "tecnico": "tickets_abiertos",
        "administrador": "sistemas_activos",
        "gerente": "objetivos_trimestrales",
    }[role]
    return f"""
<form method='post' action='/submit' class='space-y-3'>
  <input type='hidden' name='role' value='{escape(role)}'>
  <div>
    <label class='block text-sm font-medium'>Nombre</label>
    <input name='nombre' required class='mt-1 w-full rounded border p-2' placeholder='Nombre del usuario'>
  </div>
  <div>
    <label class='block text-sm font-medium'>Métrica</label>
    <input name='metric_name' class='mt-1 w-full rounded border p-2' value='{escape(default_metric)}'>
  </div>
  <div>
    <label class='block text-sm font-medium'>Valor</label>
    <input type='number' name='metric_value' class='mt-1 w-full rounded border p-2' value='1'>
  </div>
  <button class='rounded bg-emerald-600 px-4 py-2 font-semibold text-white'>Guardar</button>
</form>
"""


def handle_http(method: str, path: str, query: str, body: bytes, backend: FriolamBackend | None = None) -> tuple[str, str, str]:
    backend = backend or default_backend()

    if method == "POST" and path == "/submit":
        data = parse_qs(body.decode("utf-8"))
        try:
            role = str(data["role"][0])
            nombre = str(data["nombre"][0])
            metric_name = str(data.get("metric_name", ["valor"])[0])
            metric_value = int(data.get("metric_value", ["0"])[0])
            backend.upsert_record(role, nombre, metric_name, metric_value)
            response = render_page(
                "Registro guardado",
                "<p class='mb-3'>Dato guardado correctamente.</p><a class='text-blue-600 underline' href='/dashboard'>Ir al dashboard</a>",
                accent_color="#16a34a",
            )
            return "200 OK", response, "text/html; charset=utf-8"
        except Exception:
            return "400 Bad Request", render_page("Error", "<p>Datos inválidos en formulario.</p>", "#dc2626"), "text/html; charset=utf-8"

    if method == "GET" and path == "/":
        body_html = """
<p class='mb-4'>Friolam ahora funciona como web app completa.</p>
<ul class='list-disc pl-6'>
  <li>Captura de datos por rol mediante formularios web.</li>
  <li>Dashboard con resumen de todo lo ingresado.</li>
  <li>API disponible para integraciones.</li>
</ul>
"""
        return "200 OK", render_page("Friolam Web App", body_html, "#334155"), "text/html; charset=utf-8"

    if method == "GET" and path == "/dashboard":
        summary = backend.summary_by_role()
        records = backend.list_records(limit=30)
        cards = "".join(
            f"<div class='rounded border p-3'><p class='text-sm'>{escape(k.title())}</p><p class='text-2xl font-bold'>{v}</p></div>"
            for k, v in summary.items()
        )
        body_html = f"<div class='mb-4 grid grid-cols-1 gap-3 md:grid-cols-3'>{cards}</div>{_table(records)}"
        return "200 OK", render_page("Dashboard", body_html, "#111827"), "text/html; charset=utf-8"

    if method == "GET" and path in ["/tecnico", "/administrador", "/gerente"]:
        role = path.strip("/")
        records = backend.list_records(role=role, limit=30)
        body_html = (
            f"<h2 class='mb-4 text-xl font-semibold'>Captura - {escape(role.title())}</h2>"
            + _capture_form(role)
            + "<hr class='my-6'>"
            + _table(records)
        )
        return "200 OK", render_page(f"Vista {role.title()}", body_html, ROLE_COLORS[role]), "text/html; charset=utf-8"

    # API
    if method == "GET" and path == "/api/dashboard":
        payload = {"summary_by_role": backend.summary_by_role(), "total_records": backend.count_records()}
        return "200 OK", json.dumps(payload, ensure_ascii=False), "application/json; charset=utf-8"

    if method == "GET" and path == "/api/records":
        params = parse_qs(query)
        role = params.get("role", [None])[0]
        limit = int(params.get("limit", ["50"])[0])
        offset = int(params.get("offset", ["0"])[0])
        payload = {"total": backend.count_records(role=role), "items": backend.list_records(role=role, limit=limit, offset=offset)}
        return "200 OK", json.dumps(payload, ensure_ascii=False), "application/json; charset=utf-8"

    if method == "POST" and path == "/api/records":
        try:
            payload = json.loads(body.decode("utf-8") or "{}")
            rid = backend.upsert_record(str(payload["role"]), str(payload["nombre"]), str(payload["metric_name"]), int(payload["metric_value"]))
            return "201 Created", json.dumps({"id": rid}), "application/json; charset=utf-8"
        except Exception:
            return "400 Bad Request", json.dumps({"error": "payload inválido"}), "application/json; charset=utf-8"

    return "404 Not Found", render_page("No encontrado", "<p>Ruta no válida.</p>", "#dc2626"), "text/html; charset=utf-8"


def app(environ: dict, start_response, backend: FriolamBackend | None = None) -> list[bytes]:
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "/")
    query = environ.get("QUERY_STRING", "")
    length = int(environ.get("CONTENT_LENGTH") or 0)
    body = environ["wsgi.input"].read(length) if length else b""
    status, content, content_type = handle_http(method, path, query, body, backend)
    start_response(status, [("Content-Type", content_type)])
    return [content.encode("utf-8")]


def main() -> None:
    host, port = "0.0.0.0", 8000
    backend = default_backend()
    print(f"Friolam Web App activa en http://{host}:{port} | DB: {backend.db_file}")
    with make_server(host, port, lambda e, s: app(e, s, backend)) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
