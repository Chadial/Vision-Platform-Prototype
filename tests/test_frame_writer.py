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


if __name__ == "__main__":
    unittest.main()
