from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests import _path_setup
from vision_platform.models import CapturedFrame
from vision_platform.services.recording_service import FrameWriter
from vision_platform.apps.postprocess_tool import format_focus_report, run_focus_report


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
