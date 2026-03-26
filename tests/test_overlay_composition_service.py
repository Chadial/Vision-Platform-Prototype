from datetime import datetime, timezone
import unittest

from vision_platform.libraries.common_models import FocusOverlayData, FocusPreviewState, FocusResult, RoiDefinition
from vision_platform.models import CapturedFrame
from vision_platform.services.display_service import OverlayCompositionService
from vision_platform.services.recording_service import SnapshotFocusCapture
from vision_platform.services.stream_service import RoiStateService


def _focus_state(
    *,
    score: float,
    frame_id: int,
    roi_id: str | None,
    bounds: tuple[float, float, float, float] | None,
    anchor_x: float,
    anchor_y: float,
) -> FocusPreviewState:
    return FocusPreviewState(
        result=FocusResult(
            method="laplace",
            metric_name="laplace_variance",
            score=score,
            roi_id=roi_id,
            source_frame_id=frame_id,
        ),
        overlay=FocusOverlayData(
            score=score,
            metric_name="laplace_variance",
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            is_valid=True,
            roi_id=roi_id,
            source_frame_id=frame_id,
            region_bounds=bounds,
        ),
    )


class OverlayCompositionServiceTests(unittest.TestCase):
    def test_compose_includes_preview_snapshot_and_explicit_active_roi(self) -> None:
        preview_focus_state = _focus_state(
            score=11.0,
            frame_id=31,
            roi_id="preview-roi",
            bounds=(1.0, 1.0, 5.0, 5.0),
            anchor_x=3.0,
            anchor_y=3.0,
        )
        snapshot_focus_state = _focus_state(
            score=19.0,
            frame_id=32,
            roi_id="snapshot-roi",
            bounds=(2.0, 2.0, 6.0, 6.0),
            anchor_x=4.0,
            anchor_y=4.0,
        )
        active_roi = RoiDefinition(
            roi_id="active-roi",
            shape="rectangle",
            points=((0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)),
        )

        payload = OverlayCompositionService().compose(
            preview_focus_state=preview_focus_state,
            snapshot_focus_state=snapshot_focus_state,
            active_roi=active_roi,
        )

        self.assertIsNotNone(payload.active_roi)
        self.assertEqual(payload.active_roi.roi_id, "active-roi")
        self.assertEqual(payload.active_roi.region_bounds, (0.0, 0.0, 4.0, 4.0))
        self.assertEqual(payload.active_roi.anchor_x, 2.0)
        self.assertEqual(payload.active_roi.anchor_y, 2.0)
        self.assertIs(payload.preview_focus, preview_focus_state.overlay)
        self.assertIs(payload.snapshot_focus, snapshot_focus_state.overlay)

    def test_compose_uses_active_roi_from_state_service(self) -> None:
        roi_state_service = RoiStateService()
        roi_state_service.set_active_roi(
            RoiDefinition(
                roi_id="state-roi",
                shape="rectangle",
                points=((1.0, 1.0), (5.0, 1.0), (5.0, 5.0), (1.0, 5.0)),
            )
        )

        payload = OverlayCompositionService(roi_state_service=roi_state_service).compose()

        self.assertIsNotNone(payload.active_roi)
        self.assertEqual(payload.active_roi.roi_id, "state-roi")
        self.assertEqual(payload.active_roi.region_bounds, (1.0, 1.0, 5.0, 5.0))

    def test_compose_prefers_explicit_active_roi_over_state_service(self) -> None:
        roi_state_service = RoiStateService()
        roi_state_service.set_active_roi(
            RoiDefinition(
                roi_id="state-roi",
                shape="rectangle",
                points=((1.0, 1.0), (5.0, 1.0), (5.0, 5.0), (1.0, 5.0)),
            )
        )
        explicit_roi = RoiDefinition(
            roi_id="explicit-roi",
            shape="rectangle",
            points=((2.0, 2.0), (6.0, 2.0), (6.0, 6.0), (2.0, 6.0)),
        )

        payload = OverlayCompositionService(roi_state_service=roi_state_service).compose(active_roi=explicit_roi)

        self.assertIsNotNone(payload.active_roi)
        self.assertEqual(payload.active_roi.roi_id, "explicit-roi")
        self.assertEqual(payload.active_roi.region_bounds, (2.0, 2.0, 6.0, 6.0))

    def test_compose_can_use_snapshot_focus_capture_directly(self) -> None:
        snapshot_capture = SnapshotFocusCapture(
            frame=CapturedFrame(
                raw_frame=b"\x00" * 9,
                width=3,
                height=3,
                frame_id=33,
                pixel_format="Mono8",
                timestamp_utc=datetime.now(timezone.utc),
            ),
            focus_state=_focus_state(
                score=17.0,
                frame_id=33,
                roi_id="snapshot-roi",
                bounds=(1.0, 1.0, 4.0, 4.0),
                anchor_x=2.5,
                anchor_y=2.5,
            ),
        )

        payload = OverlayCompositionService().compose(snapshot_focus_capture=snapshot_capture)

        self.assertIsNotNone(payload.snapshot_focus)
        self.assertEqual(payload.snapshot_focus.roi_id, "snapshot-roi")
        self.assertEqual(payload.snapshot_focus.source_frame_id, 33)
        self.assertIsNone(payload.active_roi)


if __name__ == "__main__":
    unittest.main()
