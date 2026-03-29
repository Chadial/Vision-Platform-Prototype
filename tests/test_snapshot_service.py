import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

from tests import _path_setup
from vision_platform.models import CapturedFrame, SnapshotRequest
from vision_platform.services.recording_service import SnapshotService


class _FakeRawFrame:
    def __init__(self, buffer: bytes) -> None:
        self._buffer = buffer

    def get_buffer(self) -> bytes:
        return self._buffer


class SnapshotServiceTests(unittest.TestCase):
    def test_save_snapshot_writes_bmp_for_supported_visible_format(self) -> None:
        fake_driver = MagicMock()
        fake_driver.capture_snapshot.return_value = CapturedFrame(
            raw_frame=_FakeRawFrame(bytes([0, 127, 200, 255])),
            width=2,
            height=2,
            frame_id=8,
            pixel_format="Mono8",
        )

        with TemporaryDirectory() as temp_dir:
            request = SnapshotRequest(
                save_directory=Path(temp_dir),
                file_stem="capture_001",
                file_extension=".bmp",
            )

            saved_path = SnapshotService(fake_driver).save_snapshot(request)

            self.assertEqual(saved_path, Path(temp_dir) / "capture_001.bmp")
            self.assertTrue(saved_path.exists())
            self.assertEqual(saved_path.read_bytes()[:2], b"BM")
            fake_driver.capture_snapshot.assert_called_once_with()

    def test_save_snapshot_captures_frame_and_writes_to_explicit_path(self) -> None:
        fake_driver = MagicMock()
        fake_driver.capture_snapshot.return_value = CapturedFrame(
            raw_frame=_FakeRawFrame(bytes([0, 127, 200, 255])),
            width=2,
            height=2,
            frame_id=7,
            pixel_format="Mono8",
        )

        with TemporaryDirectory() as temp_dir:
            request = SnapshotRequest(
                save_directory=Path(temp_dir),
                file_stem="capture_001",
                file_extension=".png",
            )

            saved_path = SnapshotService(fake_driver).save_snapshot(request)

            self.assertEqual(saved_path, Path(temp_dir) / "capture_001.png")
            self.assertTrue(saved_path.exists())
            fake_driver.capture_snapshot.assert_called_once_with()

    def test_save_snapshot_logs_and_reraises_writer_errors(self) -> None:
        fake_driver = MagicMock()
        fake_driver.capture_snapshot.return_value = CapturedFrame(
            raw_frame=_FakeRawFrame(bytes([0, 127, 200, 255])),
            width=2,
            height=2,
            frame_id=7,
            pixel_format="Mono8",
        )
        fake_writer = MagicMock()
        fake_writer.write_frame.side_effect = RuntimeError("disk full")

        with TemporaryDirectory() as temp_dir:
            request = SnapshotRequest(
                save_directory=Path(temp_dir),
                file_stem="capture_001",
                file_extension=".png",
            )

            service = SnapshotService(fake_driver, frame_writer=fake_writer)

            with self.assertLogs("camera_app.services.snapshot_service", level="INFO") as logs:
                with self.assertRaisesRegex(RuntimeError, "disk full"):
                    service.save_snapshot(request)

            self.assertTrue(any("Saving snapshot" in message for message in logs.output))
            self.assertTrue(any("Snapshot save failed" in message for message in logs.output))

    def test_save_snapshot_rejects_invalid_file_stem(self) -> None:
        fake_driver = MagicMock()
        service = SnapshotService(fake_driver)

        with TemporaryDirectory() as temp_dir:
            request = SnapshotRequest(
                save_directory=Path(temp_dir),
                file_stem="nested/capture",
                file_extension=".png",
            )

            with self.assertRaisesRegex(ValueError, "file_stem"):
                service.save_snapshot(request)

            fake_driver.capture_snapshot.assert_not_called()


if __name__ == "__main__":
    unittest.main()
