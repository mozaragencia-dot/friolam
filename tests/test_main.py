import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from friolam.backend import FriolamBackend
from friolam.main import get_status_message
from friolam.models import Administrador, Gerente, Tecnico
from friolam.webapp import handle_path


class TestMain(unittest.TestCase):
    def test_status_message_contains_project_name(self) -> None:
        message = get_status_message()
        self.assertIn("Friolam", message)


class TestRoleModels(unittest.TestCase):
    def test_tecnico_resumen(self) -> None:
        tecnico = Tecnico("Ana", "Redes", 3)
        self.assertIn("Ana", tecnico.resumen())

    def test_administrador_resumen(self) -> None:
        admin = Administrador("Luis", 8, 2)
        self.assertIn("incidentes", admin.resumen())

    def test_gerente_resumen(self) -> None:
        gerente = Gerente("María", "Operaciones", 4)
        self.assertIn("Operaciones", gerente.resumen())


class TestBackend(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp_dir.name) / "friolam_test.db")
        self.backend = FriolamBackend(self.db_path)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_get_all_roles(self) -> None:
        roles = self.backend.get_all_roles()
        self.assertEqual(3, len(roles))

    def test_get_single_role(self) -> None:
        admin = self.backend.get_role("administrador")
        self.assertEqual("administrador", admin["role"])


class TestWebAppRoutes(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp_dir.name) / "friolam_test.db")
        self.backend = FriolamBackend(self.db_path)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_home_route(self) -> None:
        status, html, content_type = handle_path("/", backend=self.backend)
        self.assertEqual("200 OK", status)
        self.assertIn("Friolam Web App", html)
        self.assertIn("text/html", content_type)

    def test_role_routes(self) -> None:
        for route in ["/tecnico", "/administrador", "/gerente"]:
            status, html, _ = handle_path(route, backend=self.backend)
            self.assertEqual("200 OK", status)
            self.assertIn("Modelo", html)

    def test_admin_and_gerente_use_different_colors(self) -> None:
        _, admin_html, _ = handle_path("/administrador", backend=self.backend)
        _, gerente_html, _ = handle_path("/gerente", backend=self.backend)
        self.assertIn("#1d4ed8", admin_html)
        self.assertIn("#9333ea", gerente_html)

    def test_api_routes(self) -> None:
        status, payload, content_type = handle_path("/api/roles", backend=self.backend)
        self.assertEqual("200 OK", status)
        self.assertIn("administrador", payload)
        self.assertIn("application/json", content_type)

    def test_not_found(self) -> None:
        status, _, _ = handle_path("/invalida", backend=self.backend)
        self.assertEqual("404 Not Found", status)


if __name__ == "__main__":
    unittest.main()
