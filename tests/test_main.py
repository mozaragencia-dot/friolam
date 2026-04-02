import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

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


class TestWebAppRoutes(unittest.TestCase):
    def test_home_route(self) -> None:
        status, html = handle_path("/")
        self.assertEqual("200 OK", status)
        self.assertIn("Friolam Web App", html)

    def test_role_routes(self) -> None:
        for route in ["/tecnico", "/administrador", "/gerente"]:
            status, html = handle_path(route)
            self.assertEqual("200 OK", status)
            self.assertIn("Modelo", html)


    def test_admin_and_gerente_use_different_colors(self) -> None:
        _, admin_html = handle_path("/administrador")
        _, gerente_html = handle_path("/gerente")
        self.assertIn("#1d4ed8", admin_html)
        self.assertIn("#9333ea", gerente_html)
        self.assertNotEqual(admin_html, gerente_html)

    def test_not_found(self) -> None:
        status, _ = handle_path("/invalida")
        self.assertEqual("404 Not Found", status)


if __name__ == "__main__":
    unittest.main()
