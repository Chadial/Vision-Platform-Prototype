from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests import _path_setup
from camera_app.imaging import OpenCvFrameAdapter as LegacyOpenCvFrameAdapter
from vision_platform.imaging import OpenCvFrameAdapter
from vision_platform.models import CapturedFrame


class _FakeArray:
    def __init__(self, buffer: bytes, dtype: str) -> None:
        self.buffer = bytes(buffer)
        self.dtype = dtype
        self.shape = None
        self.assigned_regions: list[tuple[object, object]] = []

    def reshape(self, shape: tuple[int, ...]) -> "_FakeArray":
        self.shape = shape
        return self

    def copy(self) -> "_FakeArray":
        copied = _FakeArray(self.buffer, self.dtype)
        copied.shape = self.shape
        return copied

    def __getitem__(self, key) -> "_FakeArray":
        sliced = _FakeArray(self.buffer, self.dtype)
        sliced.shape = self.shape
        return sliced

    def __setitem__(self, key, value) -> None:
        self.assigned_regions.append((key, value))


class _FakeNumpy:
    uint8 = "uint8"
    uint16 = "uint16"

    def frombuffer(self, buffer: bytes, dtype: str) -> _FakeArray:
        return _FakeArray(buffer, dtype)

    def zeros(self, shape: tuple[int, ...], dtype: str) -> _FakeArray:
        item_size = 2 if dtype == self.uint16 else 1
        buffer_size = item_size
        for size in shape:
            buffer_size *= size
        array = _FakeArray(bytes(buffer_size), dtype)
        array.shape = shape
        return array


class _FakeCv2:
    WINDOW_NORMAL = 0
    INTER_AREA = 3
    WND_PROP_VISIBLE = 4
    FONT_HERSHEY_SIMPLEX = 0
    LINE_AA = 16

    def __init__(self) -> None:
        self.imshow_calls: list[tuple[str, _FakeArray]] = []
        self.waitkey_calls: list[int] = []
        self.waitkeyex_calls: list[int] = []
        self.imwrite_calls: list[tuple[str, _FakeArray]] = []
        self.destroyed_windows: list[str] = []
        self.destroy_all_called = False
        self.named_windows: list[tuple[str, int]] = []
        self.window_rect = (0, 0, 640, 480)
        self.window_visible = 1.0
        self.resize_calls: list[tuple[tuple[int, int], int]] = []
        self.put_text_calls: list[tuple[str, tuple[int, int]]] = []

    def imshow(self, window_name: str, image: _FakeArray) -> None:
        self.imshow_calls.append((window_name, image))

    def waitKey(self, delay_ms: int) -> int:
        self.waitkey_calls.append(delay_ms)
        return 27

    def waitKeyEx(self, delay_ms: int) -> int:
        self.waitkeyex_calls.append(delay_ms)
        return 27

    def imwrite(self, path: str, image: _FakeArray) -> bool:
        self.imwrite_calls.append((path, image))
        return True

    def destroyWindow(self, window_name: str) -> None:
        self.destroyed_windows.append(window_name)

    def destroyAllWindows(self) -> None:
        self.destroy_all_called = True

    def namedWindow(self, window_name: str, flags: int) -> None:
        self.named_windows.append((window_name, flags))

    def getWindowImageRect(self, window_name: str) -> tuple[int, int, int, int]:
        return self.window_rect

    def getWindowProperty(self, window_name: str, prop_id: int) -> float:
        return self.window_visible

    def resize(self, image: _FakeArray, size: tuple[int, int], interpolation: int) -> _FakeArray:
        resized = _FakeArray(image.buffer, image.dtype)
        if image.shape is not None and len(image.shape) == 2:
            resized.shape = (size[1], size[0])
        else:
            channels = 1 if image.shape is None else image.shape[2]
            resized.shape = (size[1], size[0], channels)
        self.resize_calls.append((size, interpolation))
        return resized

    def putText(self, image: _FakeArray, text: str, position: tuple[int, int], *_args) -> None:
        self.put_text_calls.append((text, position))


class OpenCvFrameAdapterTests(unittest.TestCase):
    def test_legacy_camera_app_imaging_package_reexports_platform_adapter(self) -> None:
        self.assertIs(LegacyOpenCvFrameAdapter, OpenCvFrameAdapter)

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
        self.assertEqual(fake_cv2.waitkeyex_calls, [5])

    def test_create_window_and_get_window_size_use_window_helpers(self) -> None:
        fake_cv2 = _FakeCv2()
        adapter = OpenCvFrameAdapter(cv2_module=fake_cv2, numpy_module=_FakeNumpy())

        adapter.create_window("Preview")
        size = adapter.get_window_image_size("Preview")

        self.assertEqual(fake_cv2.named_windows, [("Preview", fake_cv2.WINDOW_NORMAL)])
        self.assertEqual(size, (640, 480))

    def test_render_into_viewport_creates_black_canvas_and_overlay(self) -> None:
        fake_cv2 = _FakeCv2()
        adapter = OpenCvFrameAdapter(cv2_module=fake_cv2, numpy_module=_FakeNumpy())
        frame = CapturedFrame(
            raw_frame=b"\x00\x7f\xc8\xff",
            width=2,
            height=2,
            pixel_format="Mono8",
        )
        image = adapter.to_image(frame)

        viewport_image = adapter.render_into_viewport(image, viewport_width=6, viewport_height=4, scale=1.0, overlay_text="FIT 1.00x")

        self.assertEqual(viewport_image.shape, (4, 6))
        self.assertEqual(fake_cv2.resize_calls, [((2, 2), fake_cv2.INTER_AREA)])
        self.assertEqual(fake_cv2.put_text_calls, [("FIT 1.00x", (12, 28))])

    def test_is_window_visible_reads_window_property(self) -> None:
        fake_cv2 = _FakeCv2()
        adapter = OpenCvFrameAdapter(cv2_module=fake_cv2, numpy_module=_FakeNumpy())

        self.assertTrue(adapter.is_window_visible("Preview"))

        fake_cv2.window_visible = 0.0
        self.assertFalse(adapter.is_window_visible("Preview"))

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
