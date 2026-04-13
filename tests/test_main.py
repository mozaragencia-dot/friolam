import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from friolam.backend import FriolamBackend
from friolam.main import get_status_message
from friolam.webapp import handle_http


class TestMain(unittest.TestCase):
    def test_status_message_contains_project_name(self) -> None:
        self.assertIn("Friolam", get_status_message())


class TestWebAppFlow(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.backend = FriolamBackend(str(Path(self.tmp.name) / "gigante.db"))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_dashboard_html(self) -> None:
        status, html, ctype = handle_http("GET", "/dashboard", "", b"", backend=self.backend)
        self.assertEqual("200 OK", status)
        self.assertIn("Dashboard", html)
        self.assertIn("text/html", ctype)

    def test_submit_form(self) -> None:
        form = "role=tecnico&nombre=Juan&metric_name=tickets_abiertos&metric_value=8".encode("utf-8")
        status, html, _ = handle_http("POST", "/submit", "", form, backend=self.backend)
        self.assertEqual("200 OK", status)
        self.assertIn("guardado", html.lower())

    def test_role_pages(self) -> None:
        for route in ["/tecnico", "/administrador", "/gerente"]:
            status, html, _ = handle_http("GET", route, "", b"", backend=self.backend)
            self.assertEqual("200 OK", status)
            self.assertIn("Captura", html)

    def test_api_dashboard(self) -> None:
        status, payload, ctype = handle_http("GET", "/api/dashboard", "", b"", backend=self.backend)
        self.assertEqual("200 OK", status)
        data = json.loads(payload)
        self.assertIn("summary_by_role", data)
        self.assertIn("application/json", ctype)

    def test_api_post(self) -> None:
        body = json.dumps(
            {
                "role": "gerente",
                "nombre": "Carla",
                "metric_name": "objetivos_trimestrales",
                "metric_value": 15,
            }
        ).encode("utf-8")
        status, payload, _ = handle_http("POST", "/api/records", "", body, backend=self.backend)
        self.assertEqual("201 Created", status)
        rid = json.loads(payload)["id"]
        self.assertIsNotNone(self.backend.get_record(rid))


if __name__ == "__main__":
    unittest.main()
