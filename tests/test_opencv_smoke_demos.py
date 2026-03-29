from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock, patch

from tests import _path_setup
from vision_platform.apps.opencv_prototype.hardware_preview_demo import main as hardware_preview_main
from vision_platform.apps.opencv_prototype.hardware_preview_demo import run_hardware_preview_demo
from vision_platform.apps.opencv_prototype.preview_demo import run_opencv_preview_demo
from vision_platform.apps.opencv_prototype.preview_demo import main as preview_main
from vision_platform.apps.opencv_prototype.save_demo import run_opencv_save_demo


class OpenCvSmokeDemoTests(unittest.TestCase):
    def test_run_opencv_preview_demo_returns_typed_result(self) -> None:
        result = run_opencv_preview_demo(frame_limit=3, poll_interval_seconds=0.001)

        self.assertTrue(result.success)
        self.assertEqual(result.rendered_frames, 3)
        self.assertIsNone(result.snapshot_path)
        self.assertIsNone(result.saved_path)
        self.assertIsNotNone(result.preview_frame_info)
        self.assertIsNone(result.focus_preview_state)

    def test_run_opencv_preview_demo_can_return_focus_state(self) -> None:
        result = run_opencv_preview_demo(frame_limit=3, poll_interval_seconds=0.001, include_focus_state=True)

        self.assertTrue(result.success)
        self.assertEqual(result.rendered_frames, 3)
        self.assertIsNotNone(result.preview_frame_info)
        self.assertIsNotNone(result.focus_preview_state)
        self.assertTrue(result.focus_preview_state.result.is_valid)

    def test_run_opencv_save_demo_returns_saved_path_for_mono8_png(self) -> None:
        with TemporaryDirectory() as temp_dir:
            result = run_opencv_save_demo(
                save_directory=Path(temp_dir),
                file_stem="opencv_demo",
                pixel_format="Mono8",
                file_extension=".png",
            )

            self.assertTrue(result.success)
            self.assertIsNotNone(result.saved_path)
            self.assertTrue(result.saved_path.exists())
            self.assertEqual(result.saved_path.name, "opencv_demo.png")

    def test_run_opencv_save_demo_returns_saved_path_for_mono16_tiff(self) -> None:
        with TemporaryDirectory() as temp_dir:
            result = run_opencv_save_demo(
                save_directory=Path(temp_dir),
                file_stem="opencv_demo",
                pixel_format="Mono16",
                file_extension=".tiff",
            )

            self.assertTrue(result.success)
            self.assertIsNotNone(result.saved_path)
            self.assertTrue(result.saved_path.exists())
            self.assertEqual(result.saved_path.name, "opencv_demo.tiff")

    def test_preview_demo_main_returns_zero(self) -> None:
        fake_result = type("Result", (), {"rendered_frames": 3, "focus_preview_state": None})()
        print_mock = MagicMock()
        with patch("vision_platform.apps.opencv_prototype.preview_demo.configure_logging"), patch(
            "vision_platform.apps.opencv_prototype.preview_demo.run_opencv_preview_demo",
            return_value=fake_result,
        ), patch("builtins.print", print_mock), patch("argparse.ArgumentParser.parse_args", return_value=type("Args", (), {
            "sample_dir": None,
            "poll_interval_seconds": 0.03,
            "frame_limit": 3,
            "with_focus": False,
            "snapshot_save_directory": None,
            "snapshot_file_stem": "preview_snapshot",
            "snapshot_file_extension": ".png",
        })()):
            result = preview_main()

        self.assertEqual(result, 0)
        print_mock.assert_any_call(
            "Preview controls: left click=select point, "
            "i=in o=out f=fit x=crosshair r=rect e=ellipse wheel=zoom mdrag=pan c=copy q=quit, "
            "q/Esc or window close=quit"
        )

    def test_preview_demo_main_returns_one_on_failure(self) -> None:
        print_mock = MagicMock()
        with patch("vision_platform.apps.opencv_prototype.preview_demo.configure_logging"), patch(
            "vision_platform.apps.opencv_prototype.preview_demo.run_opencv_preview_demo",
            side_effect=RuntimeError("Preview startup failed"),
        ), patch("builtins.print", print_mock), patch("argparse.ArgumentParser.parse_args", return_value=type("Args", (), {
            "sample_dir": None,
            "poll_interval_seconds": 0.03,
            "frame_limit": 3,
            "with_focus": False,
            "snapshot_save_directory": None,
            "snapshot_file_stem": "preview_snapshot",
            "snapshot_file_extension": ".png",
        })()):
            result = preview_main()

        self.assertEqual(result, 1)
        print_mock.assert_any_call("ERROR: Preview demo failed: Preview startup failed")

    def test_preview_demo_main_uses_exception_type_when_message_is_empty(self) -> None:
        print_mock = MagicMock()
        with patch("vision_platform.apps.opencv_prototype.preview_demo.configure_logging"), patch(
            "vision_platform.apps.opencv_prototype.preview_demo.run_opencv_preview_demo",
            side_effect=RuntimeError(),
        ), patch("builtins.print", print_mock), patch("argparse.ArgumentParser.parse_args", return_value=type("Args", (), {
            "sample_dir": None,
            "poll_interval_seconds": 0.03,
            "frame_limit": 3,
            "with_focus": False,
            "snapshot_save_directory": None,
            "snapshot_file_stem": "preview_snapshot",
            "snapshot_file_extension": ".png",
        })()):
            result = preview_main()

        self.assertEqual(result, 1)
        print_mock.assert_any_call("ERROR: Preview demo failed: RuntimeError")

    def test_hardware_preview_demo_main_returns_zero(self) -> None:
        fake_result = type("Result", (), {
            "rendered_frames": 3,
            "preview_frame_info": type("Info", (), {"frame_id": 1, "width": 640, "height": 480, "pixel_format": "Mono8"})(),
        })()
        print_mock = MagicMock()
        with patch("vision_platform.apps.opencv_prototype.hardware_preview_demo.configure_logging"), patch(
            "vision_platform.apps.opencv_prototype.hardware_preview_demo.run_hardware_preview_demo",
            return_value=fake_result,
        ), patch("builtins.print", print_mock), patch("argparse.ArgumentParser.parse_args", return_value=type("Args", (), {
            "camera_id": None,
            "poll_interval_seconds": 0.03,
            "frame_limit": None,
            "exposure_time_us": None,
            "snapshot_save_directory": None,
            "snapshot_file_stem": "preview_snapshot",
            "snapshot_file_extension": ".png",
        })()):
            result = hardware_preview_main()

        self.assertEqual(result, 0)
        print_mock.assert_any_call(
            "Preview controls: left click=select point, "
            "i=in o=out f=fit x=crosshair r=rect e=ellipse wheel=zoom mdrag=pan c=copy q=quit, "
            "q/Esc or window close=quit"
        )

    def test_hardware_preview_demo_main_returns_one_on_failure(self) -> None:
        print_mock = MagicMock()
        with patch("vision_platform.apps.opencv_prototype.hardware_preview_demo.configure_logging"), patch(
            "vision_platform.apps.opencv_prototype.hardware_preview_demo.run_hardware_preview_demo",
            side_effect=RuntimeError("Camera not found"),
        ), patch("builtins.print", print_mock), patch("argparse.ArgumentParser.parse_args", return_value=type("Args", (), {
            "camera_id": None,
            "poll_interval_seconds": 0.03,
            "frame_limit": None,
            "exposure_time_us": None,
            "snapshot_save_directory": None,
            "snapshot_file_stem": "preview_snapshot",
            "snapshot_file_extension": ".png",
        })()):
            result = hardware_preview_main()

        self.assertEqual(result, 1)
        print_mock.assert_any_call("ERROR: Hardware preview failed: Camera not found")

    def test_run_opencv_preview_demo_shuts_down_when_start_preview_fails(self) -> None:
        driver = MagicMock()
        stream_service = MagicMock()
        stream_service.start_preview.side_effect = RuntimeError("Preview startup failed")
        preview_window = MagicMock()

        with patch("vision_platform.apps.opencv_prototype.preview_demo.SimulatedCameraDriver", return_value=driver), patch(
            "vision_platform.apps.opencv_prototype.preview_demo.CameraStreamService",
            return_value=stream_service,
        ), patch("vision_platform.apps.opencv_prototype.preview_demo.OpenCvPreviewWindow", return_value=preview_window):
            with self.assertRaisesRegex(RuntimeError, "Preview startup failed"):
                run_opencv_preview_demo(frame_limit=1, poll_interval_seconds=0.001)

        preview_window.close.assert_called_once_with()
        stream_service.stop_preview.assert_not_called()
        driver.shutdown.assert_called_once_with()

    def test_run_hardware_preview_demo_shuts_down_when_start_preview_fails(self) -> None:
        driver = MagicMock()
        camera_service = MagicMock()
        stream_service = MagicMock()
        stream_service.start_preview.side_effect = RuntimeError("Camera stream failed")
        preview_window = MagicMock()

        with patch("vision_platform.apps.opencv_prototype.hardware_preview_demo.VimbaXCameraDriver", return_value=driver), patch(
            "vision_platform.apps.opencv_prototype.hardware_preview_demo.CameraService",
            return_value=camera_service,
        ), patch(
            "vision_platform.apps.opencv_prototype.hardware_preview_demo.CameraStreamService",
            return_value=stream_service,
        ), patch("vision_platform.apps.opencv_prototype.hardware_preview_demo.OpenCvPreviewWindow", return_value=preview_window):
            with self.assertRaisesRegex(RuntimeError, "Camera stream failed"):
                run_hardware_preview_demo(frame_limit=1, poll_interval_seconds=0.001)

        preview_window.close.assert_called_once_with()
        stream_service.stop_preview.assert_not_called()
        camera_service.shutdown.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
