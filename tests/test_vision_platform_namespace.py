import unittest

from vision_platform import build_simulated_camera_subsystem
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


if __name__ == "__main__":
    unittest.main()
