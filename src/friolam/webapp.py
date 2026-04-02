"""Aplicación web minimalista (WSGI) para Friolam."""

from html import escape
from wsgiref.simple_server import make_server

from friolam.models import Administrador, Gerente, Tecnico


def get_role_data() -> dict[str, object]:
    """Return demo data for each role."""
    return {
        "tecnico": Tecnico("Ana", "Redes", 5),
        "administrador": Administrador("Luis", 12, 1),
        "gerente": Gerente("María", "Operaciones", 4),
    }


def render_page(title: str, body: str) -> str:
    """Render basic HTML page."""
    return f"""<!doctype html>
<html lang='es'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>{escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 1rem; max-width: 800px; }}
    nav a {{ margin-right: 1rem; }}
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


def handle_path(path: str) -> tuple[str, str]:
    """Resolve URL path into status and HTML response body."""
    data = get_role_data()

    if path == "/":
        body = (
            "<p>Panel principal de Friolam.</p>"
            "<ul>"
            "<li><strong>Técnico:</strong> vista operativa.</li>"
            "<li><strong>Administrador:</strong> estado de plataforma.</li>"
            "<li><strong>Gerente:</strong> seguimiento estratégico.</li>"
            "</ul>"
        )
        return "200 OK", render_page("Friolam Web App", body)

    if path == "/tecnico":
        tecnico = data["tecnico"]
        body = f"<h2>Modelo Técnico</h2><p>{escape(tecnico.resumen())}</p>"
        return "200 OK", render_page("Vista Técnico", body)

    if path == "/administrador":
        administrador = data["administrador"]
        body = f"<h2>Modelo Administrador</h2><p>{escape(administrador.resumen())}</p>"
        return "200 OK", render_page("Vista Administrador", body)

    if path == "/gerente":
        gerente = data["gerente"]
        body = f"<h2>Modelo Gerente</h2><p>{escape(gerente.resumen())}</p>"
        return "200 OK", render_page("Vista Gerente", body)

    return "404 Not Found", render_page("No encontrado", "<p>Ruta no válida.</p>")


def app(environ: dict, start_response) -> list[bytes]:
    """WSGI entrypoint."""
    path = environ.get("PATH_INFO", "/")
    status, html = handle_path(path)
    headers = [("Content-Type", "text/html; charset=utf-8")]
    start_response(status, headers)
    return [html.encode("utf-8")]


def main() -> None:
    """Run the web app server."""
    host = "0.0.0.0"
    port = 8000
    print(f"Friolam web app escuchando en http://{host}:{port}")
    with make_server(host, port, app) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
