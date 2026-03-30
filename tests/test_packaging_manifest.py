from __future__ import annotations

from pathlib import Path
import tomllib
import unittest


class PackagingManifestTests(unittest.TestCase):
    def test_pyproject_declares_python_baseline_and_cli_entrypoint(self) -> None:
        pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

        project = data["project"]

        self.assertEqual(project["requires-python"], ">=3.11")
        self.assertEqual(
            project["scripts"]["vision-platform-cli"],
            "vision_platform.apps.camera_cli:main",
        )
        self.assertIn("opencv", project["optional-dependencies"])


if __name__ == "__main__":
    unittest.main()
