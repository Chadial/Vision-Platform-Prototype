import unittest

from vision_platform import build_simulated_camera_subsystem
from vision_platform.integrations.camera import SimulatedCameraDriver
from vision_platform.libraries.common_models import FocusOverlayData, FocusRequest, FrameData, FrameMetadata, RoiDefinition
from vision_platform.libraries.focus_core import LaplaceFocusEvaluator, build_focus_overlay_data, focus_score_available
from vision_platform.libraries.roi_core import roi_bounds, roi_centroid
from vision_platform.services.recording_service import SnapshotService
from vision_platform.services.stream_service import CameraStreamService


class VisionPlatformNamespaceTests(unittest.TestCase):
    def test_platform_namespace_re_exports_existing_core_types(self) -> None:
        subsystem = build_simulated_camera_subsystem()

        self.assertIsInstance(subsystem.driver, SimulatedCameraDriver)
        self.assertIsInstance(subsystem.snapshot_service, SnapshotService)
        self.assertIsInstance(subsystem.stream_service, CameraStreamService)

    def test_foundation_models_are_importable(self) -> None:
        roi = RoiDefinition(
            roi_id="roi-1",
            shape="rectangle",
            points=((1.0, 2.0), (5.0, 7.0)),
        )
        bounds = roi_bounds(roi)
        centroid = roi_centroid(roi)

        self.assertEqual((1.0, 2.0, 5.0, 7.0), bounds)
        self.assertEqual((3.0, 4.5), centroid)
        self.assertTrue(
            focus_score_available(
                FrameData(data=b"\x00\x40\x80\xff\x80\x40\x00\x40\x80", metadata=FrameMetadata(width=3, height=3)),
                FocusRequest(roi=roi),
            )
        )
        self.assertIsInstance(LaplaceFocusEvaluator(), LaplaceFocusEvaluator)
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


if __name__ == "__main__":
    unittest.main()
