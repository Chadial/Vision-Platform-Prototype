from datetime import datetime, timezone
import unittest
from unittest.mock import MagicMock

from vision_platform.models import CapturedFrame
from vision_platform.services.stream_service import FocusPreviewService, RoiStateService
from vision_platform.libraries.common_models import RoiDefinition


def _mono8_frame_bytes(rows: list[list[int]]) -> bytes:
    return bytes(value for row in rows for value in row)


class FocusPreviewServiceTests(unittest.TestCase):
    def test_refresh_once_builds_focus_state_from_latest_preview_frame(self) -> None:
        frame = CapturedFrame(
            raw_frame=_mono8_frame_bytes(
                [
                    [0, 255, 0, 255, 0],
                    [255, 0, 255, 0, 255],
                    [0, 255, 0, 255, 0],
                    [255, 0, 255, 0, 255],
                    [0, 255, 0, 255, 0],
                ]
            ),
            width=5,
            height=5,
            frame_id=12,
            pixel_format="Mono8",
            timestamp_utc=datetime.now(timezone.utc),
        )
        preview_service = MagicMock()
        preview_service.get_latest_frame.return_value = frame

        service = FocusPreviewService(preview_service)

        focus_state = service.refresh_once()

        self.assertIsNotNone(focus_state)
        self.assertTrue(focus_state.result.is_valid)
        self.assertEqual(focus_state.result.source_frame_id, 12)
        self.assertEqual(focus_state.overlay.anchor_x, 2.5)
        self.assertEqual(focus_state.overlay.anchor_y, 2.5)
        self.assertIs(service.get_latest_focus_state(), focus_state)
        preview_service.refresh_once.assert_not_called()

    def test_refresh_once_uses_roi_overlay_anchor_when_roi_is_active(self) -> None:
        frame = CapturedFrame(
            raw_frame=_mono8_frame_bytes(
                [
                    [16, 16, 16, 0, 255, 0],
                    [16, 16, 16, 255, 0, 255],
                    [16, 16, 16, 0, 255, 0],
                    [16, 16, 16, 255, 0, 255],
                    [16, 16, 16, 0, 255, 0],
                    [16, 16, 16, 255, 0, 255],
                ]
            ),
            width=6,
            height=6,
            frame_id=13,
            pixel_format="Mono8",
            timestamp_utc=datetime.now(timezone.utc),
        )
        preview_service = MagicMock()
        preview_service.get_latest_frame.return_value = frame
        roi = RoiDefinition(
            roi_id="focus-roi",
            shape="rectangle",
            points=((3.0, 1.0), (6.0, 1.0), (6.0, 6.0), (3.0, 6.0)),
        )

        service = FocusPreviewService(preview_service)

        focus_state = service.refresh_once(roi=roi)

        self.assertIsNotNone(focus_state)
        self.assertEqual(focus_state.overlay.anchor_x, 4.5)
        self.assertEqual(focus_state.overlay.anchor_y, 3.5)
        self.assertEqual(focus_state.overlay.region_bounds, (3.0, 1.0, 6.0, 6.0))
        self.assertEqual(focus_state.overlay.roi_id, "focus-roi")

    def test_refresh_once_pulls_preview_frame_when_none_is_cached(self) -> None:
        frame = CapturedFrame(
            raw_frame=_mono8_frame_bytes(
                [
                    [0, 0, 0, 0, 0],
                    [0, 255, 255, 255, 0],
                    [0, 255, 0, 255, 0],
                    [0, 255, 255, 255, 0],
                    [0, 0, 0, 0, 0],
                ]
            ),
            width=5,
            height=5,
            frame_id=14,
            pixel_format="Mono8",
            timestamp_utc=datetime.now(timezone.utc),
        )
        preview_service = MagicMock()
        preview_service.get_latest_frame.side_effect = [None, frame]

        service = FocusPreviewService(preview_service)

        focus_state = service.refresh_once()

        self.assertIsNotNone(focus_state)
        preview_service.refresh_once.assert_called_once_with()

    def test_refresh_once_uses_active_roi_from_state_service(self) -> None:
        frame = CapturedFrame(
            raw_frame=_mono8_frame_bytes(
                [
                    [16, 16, 16, 0, 255, 0],
                    [16, 16, 16, 255, 0, 255],
                    [16, 16, 16, 0, 255, 0],
                    [16, 16, 16, 255, 0, 255],
                    [16, 16, 16, 0, 255, 0],
                    [16, 16, 16, 255, 0, 255],
                ]
            ),
            width=6,
            height=6,
            frame_id=15,
            pixel_format="Mono8",
            timestamp_utc=datetime.now(timezone.utc),
        )
        preview_service = MagicMock()
        preview_service.get_latest_frame.return_value = frame
        roi_state_service = RoiStateService()
        roi_state_service.set_active_roi(
            RoiDefinition(
                roi_id="state-roi",
                shape="rectangle",
                points=((3.0, 1.0), (6.0, 1.0), (6.0, 6.0), (3.0, 6.0)),
            )
        )

        service = FocusPreviewService(preview_service, roi_state_service=roi_state_service)

        focus_state = service.refresh_once()

        self.assertIsNotNone(focus_state)
        self.assertEqual(focus_state.result.roi_id, "state-roi")
        self.assertEqual(focus_state.overlay.roi_id, "state-roi")
        self.assertEqual(focus_state.overlay.region_bounds, (3.0, 1.0, 6.0, 6.0))

    def test_refresh_once_prefers_explicit_roi_over_state_service(self) -> None:
        frame = CapturedFrame(
            raw_frame=_mono8_frame_bytes(
                [
                    [16, 16, 16, 0, 255, 0],
                    [16, 16, 16, 255, 0, 255],
                    [16, 16, 16, 0, 255, 0],
                    [16, 16, 16, 255, 0, 255],
                    [16, 16, 16, 0, 255, 0],
                    [16, 16, 16, 255, 0, 255],
                ]
            ),
            width=6,
            height=6,
            frame_id=16,
            pixel_format="Mono8",
            timestamp_utc=datetime.now(timezone.utc),
        )
        preview_service = MagicMock()
        preview_service.get_latest_frame.return_value = frame
        roi_state_service = RoiStateService()
        roi_state_service.set_active_roi(
            RoiDefinition(
                roi_id="state-roi",
                shape="rectangle",
                points=((0.0, 0.0), (3.0, 0.0), (3.0, 3.0), (0.0, 3.0)),
            )
        )
        explicit_roi = RoiDefinition(
            roi_id="explicit-roi",
            shape="rectangle",
            points=((3.0, 1.0), (6.0, 1.0), (6.0, 6.0), (3.0, 6.0)),
        )

        service = FocusPreviewService(preview_service, roi_state_service=roi_state_service)

        focus_state = service.refresh_once(roi=explicit_roi)

        self.assertIsNotNone(focus_state)
        self.assertEqual(focus_state.result.roi_id, "explicit-roi")
        self.assertEqual(focus_state.overlay.roi_id, "explicit-roi")
        self.assertEqual(focus_state.overlay.region_bounds, (3.0, 1.0, 6.0, 6.0))


if __name__ == "__main__":
    unittest.main()
