from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from vision_platform.apps.camera_cli.camera_aliases import CameraAliasResolutionError, load_camera_aliases, resolve_camera_id


class CameraAliasTests(unittest.TestCase):
    def test_load_camera_aliases_reads_alias_mapping(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "camera_aliases.json"
            config_path.write_text(
                json.dumps({"aliases": {"lab_cam": "DEV_001"}}),
                encoding="utf-8",
            )

            aliases = load_camera_aliases(config_path)

            self.assertEqual(aliases, {"lab_cam": "DEV_001"})

    def test_resolve_camera_id_prefers_explicit_camera_id_when_no_alias_is_used(self) -> None:
        resolved_camera_id = resolve_camera_id(
            camera_id="DEV_DIRECT",
            camera_alias=None,
        )

        self.assertEqual(resolved_camera_id, "DEV_DIRECT")

    def test_resolve_camera_id_resolves_known_alias(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "camera_aliases.json"
            config_path.write_text(
                json.dumps({"aliases": {"tested_camera": "DEV_1AB22C046D81"}}),
                encoding="utf-8",
            )

            resolved_camera_id = resolve_camera_id(
                camera_id=None,
                camera_alias="tested_camera",
                config_path=config_path,
            )

            self.assertEqual(resolved_camera_id, "DEV_1AB22C046D81")

    def test_resolve_camera_id_rejects_unknown_alias(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "camera_aliases.json"
            config_path.write_text(
                json.dumps({"aliases": {"tested_camera": "DEV_1AB22C046D81"}}),
                encoding="utf-8",
            )

            with self.assertRaises(CameraAliasResolutionError) as exc_info:
                resolve_camera_id(
                    camera_id=None,
                    camera_alias="missing_camera",
                    config_path=config_path,
                )

            self.assertIn("missing_camera", str(exc_info.exception))

    def test_resolve_camera_id_rejects_combined_camera_id_and_alias(self) -> None:
        with self.assertRaises(CameraAliasResolutionError) as exc_info:
            resolve_camera_id(
                camera_id="DEV_DIRECT",
                camera_alias="tested_camera",
            )

        self.assertIn("either --camera-id or --camera-alias", str(exc_info.exception))


if __name__ == "__main__":
    unittest.main()
