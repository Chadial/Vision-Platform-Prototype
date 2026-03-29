import unittest
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

from tests import _path_setup
from vision_platform.models import CameraConfiguration, CapturedFrame, SnapshotRequest
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
            trace_lines = (Path(temp_dir) / "saved_artifact_traceability.csv").read_text(encoding="utf-8").splitlines()
            self.assertIn("# context.record_kind: saved_artifact_folder_log", trace_lines)
            self.assertIn("# run.artifact_kind: snapshot", trace_lines)
            trace_rows = list(csv.reader(line for line in trace_lines if line and not line.startswith("# ")))
            self.assertEqual(
                trace_rows[0],
                ["artifact_kind", "run_id", "image_name", "frame_id", "camera_timestamp", "system_timestamp_utc"],
            )
            self.assertEqual(trace_rows[1][0], "snapshot")
            self.assertEqual(trace_rows[1][2], "capture_001.bmp")

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

    def test_save_snapshot_writes_trace_log_with_configuration_fields(self) -> None:
        fake_driver = MagicMock()
        fake_driver.capture_snapshot.return_value = CapturedFrame(
            raw_frame=_FakeRawFrame(bytes([0, 127, 200, 255])),
            width=2,
            height=2,
            frame_id=7,
            camera_timestamp=123456,
            pixel_format="Mono8",
        )

        with TemporaryDirectory() as temp_dir:
            request = SnapshotRequest(
                save_directory=Path(temp_dir),
                file_stem="capture_001",
                file_extension=".png",
                camera_id="CAM_001",
            )

            service = SnapshotService(
                fake_driver,
                configuration_provider=lambda: CameraConfiguration(
                    exposure_time_us=2500.0,
                    gain=1.5,
                    pixel_format="Mono8",
                ),
            )
            saved_path = service.save_snapshot(request)

            trace_lines = (Path(temp_dir) / "saved_artifact_traceability.csv").read_text(encoding="utf-8").splitlines()
            self.assertIn(f"# context.save_directory: {temp_dir}", trace_lines)
            self.assertIn("# context.camera_id: CAM_001", trace_lines)
            self.assertIn("# context.pixel_format: Mono8", trace_lines)
            self.assertIn("# context.exposure_time_us: 2500.0", trace_lines)
            self.assertIn("# context.gain: 1.5", trace_lines)
            self.assertIn("# run.file_stem: capture_001", trace_lines)
            trace_rows = list(csv.reader(line for line in trace_lines if line and not line.startswith("# ")))
            self.assertEqual(trace_rows[1][2], saved_path.name)
            self.assertEqual(trace_rows[1][4], "123456")
            self.assertTrue(trace_rows[1][5])

    def test_save_snapshot_reuses_trace_log_when_context_matches(self) -> None:
        fake_driver = MagicMock()
        fake_driver.capture_snapshot.side_effect = [
            CapturedFrame(
                raw_frame=_FakeRawFrame(bytes([0, 127, 200, 255])),
                width=2,
                height=2,
                frame_id=7,
                camera_timestamp=123456,
                pixel_format="Mono8",
            ),
            CapturedFrame(
                raw_frame=_FakeRawFrame(bytes([0, 127, 200, 255])),
                width=2,
                height=2,
                frame_id=8,
                camera_timestamp=123457,
                pixel_format="Mono8",
            ),
        ]

        with TemporaryDirectory() as temp_dir:
            service = SnapshotService(
                fake_driver,
                configuration_provider=lambda: CameraConfiguration(
                    exposure_time_us=2500.0,
                    gain=1.5,
                    pixel_format="Mono8",
                ),
            )

            first_path = service.save_snapshot(
                SnapshotRequest(
                    save_directory=Path(temp_dir),
                    file_stem="capture_001",
                    file_extension=".png",
                    camera_id="CAM_001",
                )
            )
            second_path = service.save_snapshot(
                SnapshotRequest(
                    save_directory=Path(temp_dir),
                    file_stem="capture_002",
                    file_extension=".png",
                    camera_id="CAM_001",
                )
            )

            self.assertTrue(first_path.exists())
            self.assertTrue(second_path.exists())
            trace_path = Path(temp_dir) / "saved_artifact_traceability.csv"
            self.assertTrue(trace_path.exists())
            self.assertFalse((Path(temp_dir) / "saved_artifact_traceability_001.csv").exists())
            trace_lines = trace_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(trace_lines.count("# run.start"), 2)
            self.assertIn("# run.file_stem: capture_001", trace_lines)
            self.assertIn("# run.file_stem: capture_002", trace_lines)

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
