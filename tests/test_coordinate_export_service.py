import unittest

from tests import _path_setup
from vision_platform.services.display_service import CoordinateExportService


class CoordinateExportServiceTests(unittest.TestCase):
    def test_format_point_returns_stable_text(self) -> None:
        service = CoordinateExportService()

        self.assertEqual(service.format_point(1234, 567), "x=1234, y=567")


if __name__ == "__main__":
    unittest.main()
