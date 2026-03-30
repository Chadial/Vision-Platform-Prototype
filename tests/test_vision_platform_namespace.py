from pathlib import Path
import re
import unittest

from tests import _path_setup
from vision_platform import build_simulated_camera_subsystem
from vision_platform.apps.opencv_prototype.demo_result import DemoRunResult
from vision_platform.integrations.camera import SimulatedCameraDriver
from vision_platform.libraries.common_models import (
    DisplayOverlayPayload,
    FocusOverlayData,
    FocusRequest,
    FrameData,
    FrameMetadata,
    RoiDefinition,
    RoiOverlayData,
)
from vision_platform.libraries.focus_core import (
    create_focus_evaluator,
    LaplaceFocusEvaluator,
    TenengradFocusEvaluator,
    build_focus_overlay_data,
    focus_score_available,
)
from vision_platform.libraries.roi_core import roi_bounds, roi_centroid, roi_mask, roi_pixel_bounds
from vision_platform.libraries.tracking_core import EdgeProfileRequest, analyze_edge_profile
from vision_platform.services.display_service import OverlayCompositionService
from vision_platform.services.recording_service import SnapshotFocusService, SnapshotService
from vision_platform.services.stream_service import CameraStreamService, FocusPreviewService, RoiStateService
from vision_platform.apps.opencv_prototype.focus_preview_demo import run_focus_preview_demo
from vision_platform.apps.opencv_prototype.overlay_payload_demo import run_overlay_payload_demo, summarize_overlay_payload
from vision_platform.apps.postprocess_tool import format_focus_report, run_focus_report


class VisionPlatformNamespaceTests(unittest.TestCase):
    def test_opencv_demo_result_is_owned_by_platform_app_namespace(self) -> None:
        self.assertEqual(DemoRunResult.__module__, "vision_platform.apps.opencv_prototype.demo_result")

    def test_platform_namespace_re_exports_existing_core_types(self) -> None:
        subsystem = build_simulated_camera_subsystem()

        self.assertIsInstance(subsystem.driver, SimulatedCameraDriver)
        self.assertIsInstance(subsystem.snapshot_service, SnapshotService)
        self.assertIsInstance(SnapshotFocusService(subsystem.driver), SnapshotFocusService)
        self.assertIsInstance(subsystem.stream_service, CameraStreamService)
        self.assertIsInstance(FocusPreviewService(subsystem.stream_service._preview_service), FocusPreviewService)
        self.assertIsInstance(subsystem.stream_service.get_roi_state_service(), RoiStateService)
        self.assertIsInstance(OverlayCompositionService(), OverlayCompositionService)

    def test_foundation_models_are_importable(self) -> None:
        roi = RoiDefinition(
            roi_id="roi-1",
            shape="rectangle",
            points=((1.0, 2.0), (5.0, 7.0)),
        )
        bounds = roi_bounds(roi)
        centroid = roi_centroid(roi)
        pixel_bounds = roi_pixel_bounds(roi, width=8, height=8)
        masked_roi = roi_mask(roi, width=8, height=8)

        self.assertEqual((1.0, 2.0, 5.0, 7.0), bounds)
        self.assertEqual((3.0, 4.5), centroid)
        self.assertEqual((1, 2, 5, 7), pixel_bounds)
        self.assertIsNotNone(masked_roi)
        self.assertTrue(
            focus_score_available(
                FrameData(data=b"\x00\x40\x80\xff\x80\x40\x00\x40\x80", metadata=FrameMetadata(width=3, height=3)),
                FocusRequest(roi=roi),
            )
        )
        self.assertIsInstance(LaplaceFocusEvaluator(), LaplaceFocusEvaluator)
        self.assertIsInstance(TenengradFocusEvaluator(), TenengradFocusEvaluator)
        self.assertIsInstance(create_focus_evaluator("tenengrad"), TenengradFocusEvaluator)
        self.assertIsInstance(
            build_focus_overlay_data(
                focus_result=LaplaceFocusEvaluator().evaluate(
                    FrameData(
                        data=b"\x00\x40\x80\xff\x80\x40\x00\x40\x80",
                        metadata=FrameMetadata(width=3, height=3, pixel_format="Mono8"),
                    )
                ),
                frame=FrameMetadata(width=3, height=3),
                roi=roi,
            ),
            FocusOverlayData,
        )
        self.assertIsInstance(DisplayOverlayPayload(active_roi=None), DisplayOverlayPayload)
        self.assertIsInstance(RoiOverlayData(roi_id="roi", anchor_x=1.0, anchor_y=2.0), RoiOverlayData)
        self.assertTrue(
            analyze_edge_profile(
                FrameData(
                    data=b"\x00\x00\xff\xff\x00\x00\xff\xff",
                    metadata=FrameMetadata(width=4, height=2, pixel_format="Mono8"),
                ),
                request=EdgeProfileRequest(orientation="vertical"),
            ).is_valid
        )
        self.assertTrue(callable(run_focus_preview_demo))
        self.assertTrue(callable(run_overlay_payload_demo))
        self.assertTrue(callable(summarize_overlay_payload))
        self.assertTrue(callable(run_focus_report))
        self.assertTrue(callable(format_focus_report))

    def test_camera_app_imports_inside_vision_platform_are_limited_to_known_compatibility_boundaries(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        allowed_paths = {
            "src/vision_platform/apps/camera_cli/camera_cli.py",
            "src/vision_platform/apps/opencv_prototype/command_flow_demo.py",
            "src/vision_platform/apps/opencv_prototype/export_camera_capabilities.py",
            "src/vision_platform/apps/opencv_prototype/focus_preview_demo.py",
            "src/vision_platform/apps/opencv_prototype/hardware_command_flow.py",
            "src/vision_platform/apps/opencv_prototype/hardware_preview_demo.py",
            "src/vision_platform/apps/opencv_prototype/overlay_payload_demo.py",
            "src/vision_platform/apps/opencv_prototype/preview_demo.py",
            "src/vision_platform/apps/opencv_prototype/save_demo.py",
            "src/vision_platform/apps/opencv_prototype/simulated_demo.py",
            "src/vision_platform/apps/opencv_prototype/snapshot_smoke.py",
            "src/vision_platform/bootstrap.py",
            "src/vision_platform/control/command_controller.py",
            "src/vision_platform/integrations/camera/camera_driver.py",
            "src/vision_platform/models/apply_configuration_command_result.py",
            "src/vision_platform/models/apply_configuration_request.py",
            "src/vision_platform/models/camera_capability_profile.py",
            "src/vision_platform/models/camera_configuration.py",
            "src/vision_platform/models/camera_status.py",
            "src/vision_platform/models/captured_frame.py",
            "src/vision_platform/models/interval_capture_command_result.py",
            "src/vision_platform/models/interval_capture_request.py",
            "src/vision_platform/models/interval_capture_status.py",
            "src/vision_platform/models/preview_frame_info.py",
            "src/vision_platform/models/recording_command_result.py",
            "src/vision_platform/models/recording_request.py",
            "src/vision_platform/models/recording_status.py",
            "src/vision_platform/models/save_directory_command_result.py",
            "src/vision_platform/models/save_snapshot_request.py",
            "src/vision_platform/models/save_snapshot_result.py",
            "src/vision_platform/models/set_save_directory_request.py",
            "src/vision_platform/models/set_save_directory_result.py",
            "src/vision_platform/models/snapshot_command_result.py",
            "src/vision_platform/models/snapshot_request.py",
            "src/vision_platform/models/start_interval_capture_request.py",
            "src/vision_platform/models/start_recording_request.py",
            "src/vision_platform/models/stop_interval_capture_request.py",
            "src/vision_platform/models/stop_recording_request.py",
            "src/vision_platform/models/subsystem_status.py",
            "src/vision_platform/services/recording_service/camera_service.py",
            "src/vision_platform/services/recording_service/file_naming.py",
            "src/vision_platform/services/recording_service/frame_writer.py",
            "src/vision_platform/services/recording_service/interval_capture_service.py",
            "src/vision_platform/services/recording_service/recording_service.py",
            "src/vision_platform/services/recording_service/snapshot_service.py",
        }

        offending_paths: list[str] = []
        for path in (repo_root / "src" / "vision_platform").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if not re.search(r"^\s*(from|import)\s+camera_app\b", text, re.MULTILINE):
                continue
            relative_path = path.relative_to(repo_root).as_posix()
            if relative_path not in allowed_paths:
                offending_paths.append(relative_path)

        self.assertEqual(offending_paths, [])

    def test_camera_app_imports_in_tests_are_limited_to_explicit_compatibility_checks(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        allowed_test_paths = {
            "tests/test_bootstrap.py",
            "tests/test_command_controller.py",
            "tests/test_file_naming.py",
            "tests/test_frame_writer.py",
            "tests/test_opencv_adapter.py",
            "tests/test_opencv_preview.py",
        }

        offending_paths: list[str] = []
        for path in (repo_root / "tests").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if not re.search(r"^\s*(from|import)\s+camera_app\b", text, re.MULTILINE):
                continue
            relative_path = path.relative_to(repo_root).as_posix()
            if relative_path not in allowed_test_paths:
                offending_paths.append(relative_path)

        self.assertEqual(offending_paths, [])


if __name__ == "__main__":
    unittest.main()
