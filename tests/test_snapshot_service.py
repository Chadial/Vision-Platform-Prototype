import unittest
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

from tests import _path_setup
from vision_platform.libraries.common_models import RoiDefinition
from vision_platform.models import CameraConfiguration, CapturedFrame, SnapshotRequest
from vision_platform.services.recording_service import SnapshotService
from vision_platform.services.recording_service.artifact_focus_metadata_producer import ArtifactFocusMetadataProducer
from vision_platform.services.recording_service.traceability import build_trace_artifact_metadata, record_snapshot_trace
from vision_platform.services.stream_service.roi_state_service import RoiStateService


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
                [
                    "artifact_kind",
                    "run_id",
                    "image_name",
                    "frame_id",
                    "camera_timestamp",
                    "system_timestamp_utc",
                    "analysis_roi_id",
                    "analysis_roi_type",
                    "analysis_roi_data",
                    "focus_method",
                    "focus_score_frame_interval",
                    "focus_value_mean",
                    "focus_value_stddev",
                    "focus_roi_type",
                    "focus_roi_data",
                ],
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
            self.assertEqual(trace_rows[1][6:], ["", "", "", "", "", "", "", "", ""])

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

    def test_save_snapshot_continues_naming_for_reused_directory_and_same_stem(self) -> None:
        fake_driver = MagicMock()
        fake_driver.capture_snapshot.side_effect = [
            CapturedFrame(raw_frame=_FakeRawFrame(bytes([1])), width=1, height=1, frame_id=1, pixel_format="Mono8"),
            CapturedFrame(raw_frame=_FakeRawFrame(bytes([2])), width=1, height=1, frame_id=2, pixel_format="Mono8"),
        ]

        with TemporaryDirectory() as temp_dir:
            service = SnapshotService(fake_driver)
            first_path = service.save_snapshot(
                SnapshotRequest(
                    save_directory=Path(temp_dir),
                    file_stem="snapshot",
                    file_extension=".bmp",
                )
            )
            second_path = service.save_snapshot(
                SnapshotRequest(
                    save_directory=Path(temp_dir),
                    file_stem="snapshot",
                    file_extension=".bmp",
                )
            )

            self.assertEqual(first_path.name, "snapshot.bmp")
            self.assertEqual(second_path.name, "snapshot_000001.bmp")
            self.assertTrue(first_path.exists())
            self.assertTrue(second_path.exists())

    def test_record_snapshot_trace_writes_optional_analysis_and_focus_metadata(self) -> None:
        frame = CapturedFrame(
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
            saved_path = Path(temp_dir) / "capture_001.png"
            saved_path.write_bytes(b"placeholder")

            artifact_metadata = build_trace_artifact_metadata(
                analysis_roi=RoiDefinition(
                    roi_id="roi-analysis",
                    shape="rectangle",
                    points=((1, 2), (30, 40)),
                ),
                focus_method="laplace",
                focus_score_frame_interval=7,
                focus_value_mean=0.75,
                focus_value_stddev=0.05,
                focus_roi=RoiDefinition(
                    roi_id="roi-focus",
                    shape="ellipse",
                    points=((10, 20), (25, 35)),
                ),
            )

            record_snapshot_trace(
                saved_path=saved_path,
                request=request,
                frame=frame,
                configuration=CameraConfiguration(pixel_format="Mono8"),
                artifact_metadata=artifact_metadata,
            )

            trace_rows = list(
                csv.reader(
                    line
                    for line in (Path(temp_dir) / "saved_artifact_traceability.csv").read_text(encoding="utf-8").splitlines()
                    if line and not line.startswith("# ")
                )
            )
            self.assertEqual(trace_rows[1][6], "roi-analysis")
            self.assertEqual(trace_rows[1][7], "rectangle")
            self.assertEqual(trace_rows[1][8], "rectangle(1,2,30,40)")
            self.assertEqual(trace_rows[1][9], "laplace")
            self.assertEqual(trace_rows[1][10], "7")
            self.assertEqual(trace_rows[1][11], "0.75")
            self.assertEqual(trace_rows[1][12], "0.05")
            self.assertEqual(trace_rows[1][13], "ellipse")
            self.assertEqual(trace_rows[1][14], "ellipse(10,20,25,35)")

    def test_record_snapshot_trace_reuses_log_when_only_artifact_metadata_changes(self) -> None:
        with TemporaryDirectory() as temp_dir:
            request = SnapshotRequest(
                save_directory=Path(temp_dir),
                file_stem="capture",
                file_extension=".png",
                camera_id="CAM_001",
            )
            configuration = CameraConfiguration(pixel_format="Mono8")

            first_path = Path(temp_dir) / "capture_001.png"
            first_path.write_bytes(b"first")
            second_path = Path(temp_dir) / "capture_002.png"
            second_path.write_bytes(b"second")

            record_snapshot_trace(
                saved_path=first_path,
                request=request,
                frame=CapturedFrame(raw_frame=b"\x00", width=1, height=1, frame_id=1, pixel_format="Mono8"),
                configuration=configuration,
                artifact_metadata=build_trace_artifact_metadata(
                    analysis_roi=RoiDefinition(roi_id="roi-a", shape="rectangle", points=((1, 2), (3, 4))),
                ),
            )
            record_snapshot_trace(
                saved_path=second_path,
                request=request,
                frame=CapturedFrame(raw_frame=b"\x00", width=1, height=1, frame_id=2, pixel_format="Mono8"),
                configuration=configuration,
                artifact_metadata=build_trace_artifact_metadata(
                    analysis_roi=RoiDefinition(roi_id="roi-b", shape="freehand", points=((1, 1), (2, 2), (3, 3))),
                    focus_method="tenengrad",
                    focus_score_frame_interval=5,
                    focus_value_mean=1.25,
                ),
            )

            trace_path = Path(temp_dir) / "saved_artifact_traceability.csv"
            self.assertTrue(trace_path.exists())
            self.assertFalse((Path(temp_dir) / "saved_artifact_traceability_001.csv").exists())
            trace_lines = trace_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(trace_lines.count("# run.start"), 2)

    def test_build_trace_artifact_metadata_requires_aggregation_basis_for_focus_summary_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "aggregation basis"):
            build_trace_artifact_metadata(
                focus_method="laplace",
                focus_value_mean=0.75,
            )

    def test_build_trace_artifact_metadata_requires_focus_method_for_focus_summary_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "focus_method"):
            build_trace_artifact_metadata(
                focus_score_frame_interval=3,
                focus_value_mean=0.75,
            )

    def test_build_trace_artifact_metadata_rejects_non_positive_focus_score_frame_interval(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive integer"):
            build_trace_artifact_metadata(
                focus_method="laplace",
                focus_score_frame_interval=0,
            )

    def test_build_trace_artifact_metadata_rejects_non_integer_focus_score_frame_interval(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive integer"):
            build_trace_artifact_metadata(
                focus_method="laplace",
                focus_score_frame_interval="2.5",
            )

    def test_build_trace_artifact_metadata_rejects_negative_focus_value_stddev(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-negative"):
            build_trace_artifact_metadata(
                focus_method="laplace",
                focus_score_frame_interval=3,
                focus_value_stddev=-0.1,
            )

    def test_build_trace_artifact_metadata_accepts_string_focus_score_frame_interval(self) -> None:
        metadata = build_trace_artifact_metadata(
            focus_method="laplace",
            focus_score_frame_interval="3",
            focus_value_mean=0.75,
            focus_value_stddev=0.0,
        )

        self.assertEqual(metadata.focus_score_frame_interval, "3")
        self.assertEqual(metadata.focus_value_mean, "0.75")
        self.assertEqual(metadata.focus_value_stddev, "0.0")

    def test_save_snapshot_wires_focus_metadata_producer_into_trace_log(self) -> None:
        fake_driver = MagicMock()
        fake_driver.capture_snapshot.return_value = CapturedFrame(
            raw_frame=_FakeRawFrame(bytes([0, 10, 20, 30, 40, 50, 60, 70, 80])),
            width=3,
            height=3,
            frame_id=12,
            camera_timestamp=777,
            pixel_format="Mono8",
        )
        roi_state_service = RoiStateService()
        roi_state_service.set_active_roi(
            RoiDefinition(
                roi_id="roi-focus",
                shape="rectangle",
                points=((0, 0), (2, 2)),
            )
        )

        with TemporaryDirectory() as temp_dir:
            request = SnapshotRequest(
                save_directory=Path(temp_dir),
                file_stem="capture_001",
                file_extension=".bmp",
            )

            service = SnapshotService(
                fake_driver,
                artifact_focus_metadata_producer=ArtifactFocusMetadataProducer(
                    focus_method="laplace",
                    focus_score_frame_interval=3,
                    roi_state_service=roi_state_service,
                ),
            )
            service.save_snapshot(request)

            trace_rows = list(
                csv.reader(
                    line
                    for line in (Path(temp_dir) / "saved_artifact_traceability.csv").read_text(encoding="utf-8").splitlines()
                    if line and not line.startswith("# ")
                )
            )
            self.assertEqual(trace_rows[1][7], "rectangle")
            self.assertEqual(trace_rows[1][8], "rectangle(0,0,2,2)")
            self.assertEqual(trace_rows[1][9], "laplace")
            self.assertEqual(trace_rows[1][10], "3")
            self.assertTrue(trace_rows[1][11])
            self.assertTrue(trace_rows[1][12])
            self.assertEqual(trace_rows[1][13], "rectangle")
            self.assertEqual(trace_rows[1][14], "rectangle(0,0,2,2)")

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
