from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests import _path_setup
from camera_app.models.captured_frame import CapturedFrame
from camera_app.storage.frame_writer import FrameWriter


class _FakeRawFrame:
    def __init__(self, buffer: bytes) -> None:
        self._buffer = buffer

    def get_buffer(self) -> bytes:
        return self._buffer


class _FakeOpenCvAdapter:
    def __init__(self) -> None:
        self.calls: list[tuple[CapturedFrame, Path, bool]] = []

    def save_lossless_grayscale(self, frame: CapturedFrame, target_path: Path, create_directories: bool = True) -> Path:
        self.calls.append((frame, target_path, create_directories))
        if create_directories:
            target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(b"opencv")
        return target_path


class FrameWriterTests(unittest.TestCase):
    def test_write_frame_creates_png_file_for_mono8_frame(self) -> None:
        frame = CapturedFrame(
            raw_frame=_FakeRawFrame(bytes([0, 127, 200, 255])),
            width=2,
            height=2,
            pixel_format="Mono8",
        )

        with TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "snapshot.png"

            saved_path = FrameWriter().write_frame(frame, target_path)

            self.assertEqual(saved_path, target_path)
            self.assertTrue(target_path.exists())
            self.assertEqual(target_path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_write_frame_creates_parent_directory_when_requested(self) -> None:
        frame = CapturedFrame(
            raw_frame=_FakeRawFrame(bytes([1, 2, 3, 4])),
            width=2,
            height=2,
            pixel_format="Mono8",
        )

        with TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "nested" / "snapshot.png"

            FrameWriter().write_frame(frame, target_path, create_directories=True)

            self.assertTrue(target_path.exists())

    def test_write_frame_raises_for_unsupported_extension(self) -> None:
        frame = CapturedFrame(
            raw_frame=_FakeRawFrame(bytes([1, 2, 3, 4])),
            width=2,
            height=2,
            pixel_format="Mono8",
        )

        with TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "snapshot.jpg"

            with self.assertRaisesRegex(RuntimeError, "Unsupported snapshot file extension"):
                FrameWriter().write_frame(frame, target_path)

    def test_write_frame_raises_for_mono16_png_without_optional_opencv_path(self) -> None:
        frame = CapturedFrame(
            raw_frame=_FakeRawFrame(b"\x01\x00\x02\x00\x03\x00\x04\x00"),
            width=2,
            height=2,
            pixel_format="Mono16",
        )

        with TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "snapshot.png"

            with self.assertRaisesRegex(RuntimeError, "requires the optional OpenCV path"):
                FrameWriter().write_frame(frame, target_path)

    def test_write_frame_uses_optional_opencv_path_for_mono16_png(self) -> None:
        frame = CapturedFrame(
            raw_frame=_FakeRawFrame(b"\x01\x00\x02\x00\x03\x00\x04\x00"),
            width=2,
            height=2,
            pixel_format="Mono16",
        )
        adapter = _FakeOpenCvAdapter()

        with TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "snapshot.png"

            saved_path = FrameWriter(opencv_adapter=adapter).write_frame(frame, target_path)

            self.assertEqual(saved_path, target_path)
            self.assertEqual(len(adapter.calls), 1)
            self.assertTrue(target_path.exists())

    def test_write_frame_uses_optional_opencv_path_for_tiff_output(self) -> None:
        frame = CapturedFrame(
            raw_frame=_FakeRawFrame(bytes([1, 2, 3, 4])),
            width=2,
            height=2,
            pixel_format="Mono8",
        )
        adapter = _FakeOpenCvAdapter()

        with TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "snapshot.tiff"

            saved_path = FrameWriter(opencv_adapter=adapter).write_frame(frame, target_path)

            self.assertEqual(saved_path, target_path)
            self.assertEqual(len(adapter.calls), 1)
            self.assertEqual(adapter.calls[0][1], target_path)

    def test_write_frame_rejects_tiff_for_rgb_output(self) -> None:
        frame = CapturedFrame(
            raw_frame=_FakeRawFrame(bytes([1, 2, 3])),
            width=1,
            height=1,
            pixel_format="Rgb8",
        )
        adapter = _FakeOpenCvAdapter()

        with TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "snapshot.tiff"

            with self.assertRaisesRegex(RuntimeError, "not supported for TIFF output"):
                FrameWriter(opencv_adapter=adapter).write_frame(frame, target_path)

            self.assertEqual(len(adapter.calls), 0)


if __name__ == "__main__":
    unittest.main()
