from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests import _path_setup
from vision_platform.libraries.common_models import RoiDefinition
from vision_platform.models import CapturedFrame
from vision_platform.services.recording_service import FrameWriter
from vision_platform.apps.postprocess_tool import format_focus_report, run_focus_report
from vision_platform.services.recording_service.traceability import build_trace_artifact_metadata, record_snapshot_trace
from vision_platform.models import CameraConfiguration, SnapshotRequest


class _FakeRawFrame:
    def __init__(self, buffer: bytes) -> None:
        self._buffer = buffer

    def get_buffer(self) -> bytes:
        return self._buffer


class PostprocessToolTests(unittest.TestCase):
    def test_run_focus_report_returns_entries_for_pgm_and_ppm_inputs(self) -> None:
        with TemporaryDirectory() as temp_dir:
            sample_dir = Path(temp_dir)
            (sample_dir / "frame_a.pgm").write_bytes(b"P5\n3 3\n255\n\x00\x40\x80\xff\x80\x40\x00\x40\x80")
            (sample_dir / "frame_b.ppm").write_bytes(
                b"P6\n3 3\n255\n"
                b"\x00\x00\x00\x40\x40\x40\x80\x80\x80"
                b"\xff\xff\xff\x80\x80\x80\x40\x40\x40"
                b"\x00\x00\x00\x40\x40\x40\x80\x80\x80"
            )

            entries = run_focus_report(sample_dir, method="tenengrad")

        self.assertEqual([entry.source_path.name for entry in entries], ["frame_a.pgm", "frame_b.ppm"])
        self.assertTrue(all(entry.method == "tenengrad" for entry in entries))
        self.assertTrue(all(entry.is_valid for entry in entries))
        self.assertEqual(entries[0].pixel_format, "Mono8")
        self.assertEqual(entries[1].pixel_format, "Rgb8")

    def test_run_focus_report_returns_entries_for_saved_bmp_inputs(self) -> None:
        with TemporaryDirectory() as temp_dir:
            sample_dir = Path(temp_dir)
            writer = FrameWriter()
            writer.write_frame(
                CapturedFrame(
                    raw_frame=_FakeRawFrame(bytes([0, 64, 128, 255, 128, 64, 0, 64, 128])),
                    width=3,
                    height=3,
                    pixel_format="Mono8",
                ),
                sample_dir / "frame_a.bmp",
            )
            writer.write_frame(
                CapturedFrame(
                    raw_frame=_FakeRawFrame(
                        bytes(
                            [
                                255, 0, 0,
                                64, 64, 64,
                                0, 0, 255,
                                255, 255, 255,
                                128, 128, 128,
                                32, 32, 32,
                                0, 255, 0,
                                64, 128, 255,
                                255, 128, 64,
                            ]
                        )
                    ),
                    width=3,
                    height=3,
                    pixel_format="Rgb8",
                ),
                sample_dir / "frame_b.bmp",
            )

            entries = run_focus_report(sample_dir, method="laplace")

        self.assertEqual([entry.source_path.name for entry in entries], ["frame_a.bmp", "frame_b.bmp"])
        self.assertTrue(all(entry.is_valid for entry in entries))
        self.assertEqual(entries[0].pixel_format, "Mono8")
        self.assertEqual(entries[1].pixel_format, "Bgr8")
        self.assertIsNone(entries[0].artifact_kind)
        self.assertIsNone(entries[1].run_id)

    def test_run_focus_report_joins_traceability_metadata_for_saved_bmp_inputs(self) -> None:
        with TemporaryDirectory() as temp_dir:
            sample_dir = Path(temp_dir)
            writer = FrameWriter()
            target_path = sample_dir / "frame_a.bmp"
            frame = CapturedFrame(
                raw_frame=_FakeRawFrame(bytes([0, 64, 128, 255, 128, 64, 0, 64, 128])),
                width=3,
                height=3,
                frame_id=21,
                camera_timestamp=4242,
                pixel_format="Mono8",
            )
            writer.write_frame(frame, target_path)
            record_snapshot_trace(
                saved_path=target_path,
                request=SnapshotRequest(
                    save_directory=sample_dir,
                    file_stem="frame_a",
                    file_extension=".bmp",
                    camera_id="CAM_001",
                ),
                frame=frame,
                configuration=CameraConfiguration(pixel_format="Mono8"),
                artifact_metadata=build_trace_artifact_metadata(
                    analysis_roi=RoiDefinition(
                        roi_id="roi-analysis",
                        shape="rectangle",
                        points=((1, 2), (30, 40)),
                    ),
                    focus_method="laplace",
                    focus_value_mean=0.75,
                    focus_value_stddev=0.05,
                ),
            )

            entry = run_focus_report(sample_dir, method="laplace")[0]
            report = format_focus_report([entry])

        self.assertEqual(entry.artifact_kind, "snapshot")
        self.assertEqual(entry.run_id, "frame_a")
        self.assertEqual(entry.frame_id, "21")
        self.assertEqual(entry.camera_timestamp, "4242")
        self.assertEqual(entry.analysis_roi_type, "rectangle")
        self.assertEqual(entry.analysis_roi_data, "rectangle(1,2,30,40)")
        self.assertEqual(entry.focus_method, "laplace")
        self.assertEqual(entry.focus_value_mean, "0.75")
        self.assertEqual(entry.focus_value_stddev, "0.05")
        self.assertIn("artifact_kind=snapshot", report)
        self.assertIn("run_id=frame_a", report)
        self.assertIn("analysis_roi_type=rectangle", report)
        self.assertIn("focus_method=laplace", report)

    def test_run_focus_report_degrades_when_only_some_images_have_trace_rows(self) -> None:
        with TemporaryDirectory() as temp_dir:
            sample_dir = Path(temp_dir)
            writer = FrameWriter()
            frame_a = CapturedFrame(
                raw_frame=_FakeRawFrame(bytes([0, 64, 128, 255, 128, 64, 0, 64, 128])),
                width=3,
                height=3,
                frame_id=1,
                camera_timestamp=1001,
                pixel_format="Mono8",
            )
            frame_b = CapturedFrame(
                raw_frame=_FakeRawFrame(bytes([1, 65, 129, 254, 127, 63, 1, 65, 129])),
                width=3,
                height=3,
                pixel_format="Mono8",
            )
            writer.write_frame(frame_a, sample_dir / "frame_a.bmp")
            writer.write_frame(frame_b, sample_dir / "frame_b.bmp")
            record_snapshot_trace(
                saved_path=sample_dir / "frame_a.bmp",
                request=SnapshotRequest(
                    save_directory=sample_dir,
                    file_stem="frame_a",
                    file_extension=".bmp",
                ),
                frame=frame_a,
                configuration=CameraConfiguration(pixel_format="Mono8"),
                artifact_metadata=build_trace_artifact_metadata(
                    analysis_roi=RoiDefinition(
                        roi_id="roi-analysis",
                        shape="freehand",
                        points=((1, 1), (2, 2), (3, 3)),
                    ),
                ),
            )

            entries = run_focus_report(sample_dir, method="laplace")

        self.assertEqual([entry.source_path.name for entry in entries], ["frame_a.bmp", "frame_b.bmp"])
        self.assertEqual(entries[0].artifact_kind, "snapshot")
        self.assertEqual(entries[0].analysis_roi_type, "freehand")
        self.assertIsNone(entries[1].artifact_kind)
        self.assertIsNone(entries[1].analysis_roi_type)

    def test_format_focus_report_renders_compact_lines(self) -> None:
        with TemporaryDirectory() as temp_dir:
            sample_dir = Path(temp_dir)
            (sample_dir / "frame_a.pgm").write_bytes(b"P5\n3 3\n255\n\x00\x40\x80\xff\x80\x40\x00\x40\x80")

            report = format_focus_report(run_focus_report(sample_dir))

        self.assertIn("frame_a.pgm: method=laplace", report)
        self.assertIn("valid=true", report)
        self.assertIn("size=3x3", report)

    def test_run_focus_report_rejects_empty_directory(self) -> None:
        with TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, "does not contain any .pgm, .ppm, or .bmp"):
                run_focus_report(Path(temp_dir))

    def test_run_focus_report_rejects_unsupported_bmp_shape(self) -> None:
        with TemporaryDirectory() as temp_dir:
            sample_dir = Path(temp_dir)
            (sample_dir / "broken.bmp").write_bytes(b"BM\x00\x00\x00")

            with self.assertRaisesRegex(RuntimeError, "Unsupported BMP input"):
                run_focus_report(sample_dir)


if __name__ == "__main__":
    unittest.main()
