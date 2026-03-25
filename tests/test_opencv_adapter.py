from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests import _path_setup
from camera_app.imaging.opencv_adapter import OpenCvFrameAdapter
from camera_app.models.captured_frame import CapturedFrame


class _FakeArray:
    def __init__(self, buffer: bytes, dtype: str) -> None:
        self.buffer = bytes(buffer)
        self.dtype = dtype
        self.shape = None

    def reshape(self, shape: tuple[int, ...]) -> "_FakeArray":
        self.shape = shape
        return self

    def copy(self) -> "_FakeArray":
        copied = _FakeArray(self.buffer, self.dtype)
        copied.shape = self.shape
        return copied


class _FakeNumpy:
    uint8 = "uint8"
    uint16 = "uint16"

    def frombuffer(self, buffer: bytes, dtype: str) -> _FakeArray:
        return _FakeArray(buffer, dtype)


class _FakeCv2:
    def __init__(self) -> None:
        self.imshow_calls: list[tuple[str, _FakeArray]] = []
        self.waitkey_calls: list[int] = []
        self.imwrite_calls: list[tuple[str, _FakeArray]] = []
        self.destroyed_windows: list[str] = []
        self.destroy_all_called = False

    def imshow(self, window_name: str, image: _FakeArray) -> None:
        self.imshow_calls.append((window_name, image))

    def waitKey(self, delay_ms: int) -> int:
        self.waitkey_calls.append(delay_ms)
        return 27

    def imwrite(self, path: str, image: _FakeArray) -> bool:
        self.imwrite_calls.append((path, image))
        return True

    def destroyWindow(self, window_name: str) -> None:
        self.destroyed_windows.append(window_name)

    def destroyAllWindows(self) -> None:
        self.destroy_all_called = True


class OpenCvFrameAdapterTests(unittest.TestCase):
    def test_to_image_converts_mono16_buffer_without_normalization(self) -> None:
        adapter = OpenCvFrameAdapter(cv2_module=_FakeCv2(), numpy_module=_FakeNumpy())
        frame = CapturedFrame(
            raw_frame=b"\x01\x00\x02\x00\x03\x00\x04\x00",
            width=2,
            height=2,
            pixel_format="Mono16",
        )

        image = adapter.to_image(frame)

        self.assertEqual(image.dtype, "uint16")
        self.assertEqual(image.shape, (2, 2))
        self.assertEqual(image.buffer, b"\x01\x00\x02\x00\x03\x00\x04\x00")

    def test_show_frame_calls_imshow_and_waitkey(self) -> None:
        fake_cv2 = _FakeCv2()
        adapter = OpenCvFrameAdapter(cv2_module=fake_cv2, numpy_module=_FakeNumpy())
        frame = CapturedFrame(
            raw_frame=b"\x00\x7f\xc8\xff",
            width=2,
            height=2,
            pixel_format="Mono8",
        )

        key_code = adapter.show_frame("Preview", frame, delay_ms=5)

        self.assertEqual(key_code, 27)
        self.assertEqual(len(fake_cv2.imshow_calls), 1)
        self.assertEqual(fake_cv2.imshow_calls[0][0], "Preview")
        self.assertEqual(fake_cv2.waitkey_calls, [5])

    def test_save_lossless_grayscale_writes_png_via_cv2(self) -> None:
        fake_cv2 = _FakeCv2()
        adapter = OpenCvFrameAdapter(cv2_module=fake_cv2, numpy_module=_FakeNumpy())
        frame = CapturedFrame(
            raw_frame=b"\x00\x01\x00\x02\x00\x03\x00\x04",
            width=2,
            height=2,
            pixel_format="Mono16",
        )

        with TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "nested" / "capture.png"

            saved_path = adapter.save_lossless_grayscale(frame, target_path)

            self.assertEqual(saved_path, target_path)
            self.assertTrue(target_path.parent.exists())
            self.assertEqual(len(fake_cv2.imwrite_calls), 1)
            self.assertEqual(fake_cv2.imwrite_calls[0][0], str(target_path))
            self.assertEqual(fake_cv2.imwrite_calls[0][1].dtype, "uint16")

    def test_save_lossless_grayscale_rejects_color_pixel_format(self) -> None:
        adapter = OpenCvFrameAdapter(cv2_module=_FakeCv2(), numpy_module=_FakeNumpy())
        frame = CapturedFrame(
            raw_frame=b"\x01\x02\x03",
            width=1,
            height=1,
            pixel_format="Rgb8",
        )

        with TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "capture.tiff"

            with self.assertRaisesRegex(RuntimeError, "not supported for lossless grayscale"):
                adapter.save_lossless_grayscale(frame, target_path)


if __name__ == "__main__":
    unittest.main()
