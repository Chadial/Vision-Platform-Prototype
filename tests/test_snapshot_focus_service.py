from datetime import datetime, timezone
import unittest
from unittest.mock import MagicMock

from vision_platform.libraries.common_models import RoiDefinition
from vision_platform.models import CapturedFrame
from vision_platform.services.recording_service import SnapshotFocusCapture, SnapshotFocusService
from vision_platform.services.stream_service import RoiStateService


def _mono8_frame_bytes(rows: list[list[int]]) -> bytes:
    return bytes(value for row in rows for value in row)


class SnapshotFocusServiceTests(unittest.TestCase):
    def test_capture_focus_state_uses_explicit_roi(self) -> None:
        driver = MagicMock()
        driver.capture_snapshot.return_value = CapturedFrame(
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
            frame_id=21,
            pixel_format="Mono8",
            timestamp_utc=datetime.now(timezone.utc),
        )
        roi = RoiDefinition(
            roi_id="snapshot-roi",
            shape="rectangle",
            points=((3.0, 1.0), (6.0, 1.0), (6.0, 6.0), (3.0, 6.0)),
        )

        capture = SnapshotFocusService(driver).capture_focus_state(roi=roi)

        self.assertIsInstance(capture, SnapshotFocusCapture)
        self.assertEqual(capture.frame.frame_id, 21)
        self.assertEqual(capture.focus_state.result.roi_id, "snapshot-roi")
        self.assertEqual(capture.focus_state.overlay.roi_id, "snapshot-roi")
        self.assertEqual(capture.focus_state.overlay.region_bounds, (3.0, 1.0, 6.0, 6.0))
        driver.capture_snapshot.assert_called_once_with()

    def test_capture_focus_state_uses_active_roi_from_state_service(self) -> None:
        driver = MagicMock()
        driver.capture_snapshot.return_value = CapturedFrame(
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
            frame_id=22,
            pixel_format="Mono8",
            timestamp_utc=datetime.now(timezone.utc),
        )
        roi_state_service = RoiStateService()
        roi_state_service.set_active_roi(
            RoiDefinition(
                roi_id="shared-roi",
                shape="rectangle",
                points=((3.0, 1.0), (6.0, 1.0), (6.0, 6.0), (3.0, 6.0)),
            )
        )

        capture = SnapshotFocusService(driver, roi_state_service=roi_state_service).capture_focus_state()

        self.assertEqual(capture.focus_state.result.roi_id, "shared-roi")
        self.assertEqual(capture.focus_state.overlay.roi_id, "shared-roi")
        self.assertEqual(capture.focus_state.overlay.region_bounds, (3.0, 1.0, 6.0, 6.0))

    def test_capture_focus_state_prefers_explicit_roi_over_state_service(self) -> None:
        driver = MagicMock()
        driver.capture_snapshot.return_value = CapturedFrame(
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
            frame_id=23,
            pixel_format="Mono8",
            timestamp_utc=datetime.now(timezone.utc),
        )
        roi_state_service = RoiStateService()
        roi_state_service.set_active_roi(
            RoiDefinition(
                roi_id="shared-roi",
                shape="rectangle",
                points=((0.0, 0.0), (3.0, 0.0), (3.0, 3.0), (0.0, 3.0)),
            )
        )
        explicit_roi = RoiDefinition(
            roi_id="explicit-roi",
            shape="rectangle",
            points=((3.0, 1.0), (6.0, 1.0), (6.0, 6.0), (3.0, 6.0)),
        )

        capture = SnapshotFocusService(
            driver,
            roi_state_service=roi_state_service,
        ).capture_focus_state(roi=explicit_roi)

        self.assertEqual(capture.focus_state.result.roi_id, "explicit-roi")
        self.assertEqual(capture.focus_state.overlay.roi_id, "explicit-roi")
        self.assertEqual(capture.focus_state.overlay.region_bounds, (3.0, 1.0, 6.0, 6.0))


if __name__ == "__main__":
    unittest.main()
