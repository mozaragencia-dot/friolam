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


class TestBackendGigante(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.backend = FriolamBackend(str(Path(self.tmp.name) / "gigante.db"))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_seed_and_count(self) -> None:
        self.assertGreaterEqual(self.backend.count_records(), 3)

    def test_upsert_and_get(self) -> None:
        rid = self.backend.upsert_record("tecnico", "Pedro", "tickets_abiertos", 99)
        rec = self.backend.get_record(rid)
        self.assertIsNotNone(rec)
        self.assertEqual("Pedro", rec["nombre"])

    def test_summary_by_role(self) -> None:
        summary = self.backend.summary_by_role()
        self.assertIn("tecnico", summary)


class TestWebApp(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.backend = FriolamBackend(str(Path(self.tmp.name) / "gigante.db"))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_home_html(self) -> None:
        status, html, ctype = handle_http("GET", "/", "", b"", backend=self.backend)
        self.assertEqual("200 OK", status)
        self.assertIn("cdn.tailwindcss.com", html)
        self.assertIn("text/html", ctype)

    def test_role_color_difference(self) -> None:
        _, admin_html, _ = handle_http("GET", "/administrador", "", b"", backend=self.backend)
        _, gerente_html, _ = handle_http("GET", "/gerente", "", b"", backend=self.backend)
        self.assertIn("#1d4ed8", admin_html)
        self.assertIn("#9333ea", gerente_html)

    def test_ionic_route(self) -> None:
        status, html, _ = handle_http("GET", "/ionic", "", b"", backend=self.backend)
        self.assertEqual("200 OK", status)
        self.assertIn("@ionic/core", html)

    def test_api_dashboard(self) -> None:
        status, payload, _ = handle_http("GET", "/api/dashboard", "", b"", backend=self.backend)
        self.assertEqual("200 OK", status)
        self.assertIn("summary_by_role", payload)

    def test_api_list(self) -> None:
        status, payload, ctype = handle_http("GET", "/api/records", "limit=10", b"", backend=self.backend)
        data = json.loads(payload)
        self.assertEqual("200 OK", status)
        self.assertIn("items", data)
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
        rec_id = json.loads(payload)["id"]
        self.assertIsNotNone(self.backend.get_record(rec_id))


if __name__ == "__main__":
    unittest.main()
