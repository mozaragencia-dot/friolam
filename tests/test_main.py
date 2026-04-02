import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from friolam.main import get_status_message


class TestMain(unittest.TestCase):
    def test_status_message_contains_project_name(self) -> None:
        message = get_status_message()
        self.assertIn("Friolam", message)

    def test_status_message_contains_version_marker(self) -> None:
        message = get_status_message()
        self.assertIn("v", message)


if __name__ == "__main__":
    unittest.main()
