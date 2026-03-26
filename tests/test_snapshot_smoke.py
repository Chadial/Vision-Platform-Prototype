from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock

from tests import _path_setup
from vision_platform.models import CameraConfiguration
from vision_platform.apps.opencv_prototype.snapshot_smoke import run_snapshot_smoke


class SnapshotSmokeTests(unittest.TestCase):
    def test_run_snapshot_smoke_initializes_cam2_and_saves_snapshot(self) -> None:
        fake_camera_service = MagicMock()
        fake_snapshot_service = MagicMock()

        with TemporaryDirectory() as temp_dir:
            expected_path = Path(temp_dir) / "smoke_snapshot.png"
            fake_snapshot_service.save_snapshot.return_value = expected_path

            saved_path = run_snapshot_smoke(
                camera_id="cam2",
                save_directory=Path(temp_dir),
                file_stem="smoke_snapshot",
                configuration=CameraConfiguration(pixel_format="Mono8"),
                camera_service=fake_camera_service,
                snapshot_service=fake_snapshot_service,
            )

            self.assertEqual(saved_path, expected_path)
            fake_camera_service.initialize.assert_called_once_with(camera_id="cam2")
            fake_camera_service.apply_configuration.assert_called_once()
            request = fake_snapshot_service.save_snapshot.call_args.args[0]
            self.assertEqual(request.camera_id, "cam2")
            self.assertEqual(request.save_directory, Path(temp_dir))
            self.assertEqual(request.file_stem, "smoke_snapshot")
            fake_camera_service.shutdown.assert_called_once_with()

    def test_run_snapshot_smoke_shuts_down_when_snapshot_fails(self) -> None:
        fake_camera_service = MagicMock()
        fake_snapshot_service = MagicMock()
        fake_snapshot_service.save_snapshot.side_effect = RuntimeError("snapshot failed")

        with TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(RuntimeError, "snapshot failed"):
                run_snapshot_smoke(
                    camera_id="cam2",
                    save_directory=Path(temp_dir),
                    file_stem="smoke_snapshot",
                    camera_service=fake_camera_service,
                    snapshot_service=fake_snapshot_service,
                )

        fake_camera_service.shutdown.assert_called_once_with()

    def test_run_snapshot_smoke_rejects_partial_service_injection(self) -> None:
        with TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, "both camera_service and snapshot_service, or neither"):
                run_snapshot_smoke(
                    camera_id="cam2",
                    save_directory=Path(temp_dir),
                    file_stem="smoke_snapshot",
                    camera_service=MagicMock(),
                    snapshot_service=None,
                )


if __name__ == "__main__":
    unittest.main()
