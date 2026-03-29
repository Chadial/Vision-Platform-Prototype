from datetime import datetime, timezone
import unittest

from tests import _path_setup
from vision_platform.libraries.common_models import FrameData, FrameMetadata, RoiDefinition
from vision_platform.libraries.tracking_core import EdgeProfileRequest, analyze_edge_profile
from vision_platform.models import CapturedFrame


def _mono8_frame_bytes(rows: list[list[int]]) -> bytes:
    return bytes(value for row in rows for value in row)


class TrackingCoreTests(unittest.TestCase):
    def test_vertical_edge_profile_finds_dominant_column_transition(self) -> None:
        frame = FrameData(
            data=_mono8_frame_bytes(
                [
                    [0, 0, 255, 255, 255],
                    [0, 0, 255, 255, 255],
                    [0, 0, 255, 255, 255],
                    [0, 0, 255, 255, 255],
                ]
            ),
            metadata=FrameMetadata(width=5, height=4, pixel_format="Mono8", frame_id=41),
        )

        result = analyze_edge_profile(frame, request=EdgeProfileRequest(orientation="vertical"))

        self.assertTrue(result.is_valid)
        self.assertEqual(result.orientation, "vertical")
        self.assertEqual(result.source_frame_id, 41)
        self.assertEqual(result.dominant_edge_index, 1)
        self.assertAlmostEqual(result.dominant_edge_position, 1.5)
        self.assertGreater(result.dominant_edge_strength, 0.0)

    def test_horizontal_edge_profile_finds_dominant_row_transition(self) -> None:
        frame = FrameData(
            data=_mono8_frame_bytes(
                [
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [255, 255, 255, 255],
                    [255, 255, 255, 255],
                ]
            ),
            metadata=FrameMetadata(width=4, height=4, pixel_format="Mono8", frame_id=42),
        )

        result = analyze_edge_profile(frame, request=EdgeProfileRequest(orientation="horizontal"))

        self.assertTrue(result.is_valid)
        self.assertEqual(result.dominant_edge_index, 1)
        self.assertAlmostEqual(result.dominant_edge_position, 1.5)
        self.assertGreater(result.dominant_edge_strength, 0.0)

    def test_edge_profile_can_limit_analysis_to_roi(self) -> None:
        frame = FrameData(
            data=_mono8_frame_bytes(
                [
                    [16, 16, 16, 16, 16, 16],
                    [16, 16, 0, 0, 255, 255],
                    [16, 16, 0, 0, 255, 255],
                    [16, 16, 0, 0, 255, 255],
                    [16, 16, 0, 0, 255, 255],
                    [16, 16, 16, 16, 16, 16],
                ]
            ),
            metadata=FrameMetadata(width=6, height=6, pixel_format="Mono8", frame_id=43),
        )
        roi = RoiDefinition(
            roi_id="edge-roi",
            shape="rectangle",
            points=((2.0, 1.0), (6.0, 1.0), (6.0, 5.0), (2.0, 5.0)),
        )

        result = analyze_edge_profile(
            frame,
            request=EdgeProfileRequest(orientation="vertical", roi=roi),
        )

        self.assertTrue(result.is_valid)
        self.assertEqual(result.roi_id, "edge-roi")
        self.assertEqual(result.dominant_edge_index, 3)
        self.assertAlmostEqual(result.dominant_edge_position, 3.5)
        self.assertGreater(result.dominant_edge_strength, 0.0)

    def test_edge_profile_accepts_captured_frame_input(self) -> None:
        frame = CapturedFrame(
            raw_frame=_mono8_frame_bytes(
                [
                    [0, 0, 255, 255],
                    [0, 0, 255, 255],
                    [0, 0, 255, 255],
                    [0, 0, 255, 255],
                ]
            ),
            width=4,
            height=4,
            frame_id=44,
            pixel_format="Mono8",
            timestamp_utc=datetime.now(timezone.utc),
        )

        result = analyze_edge_profile(frame)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.source_frame_id, 44)

    def test_edge_profile_reports_invalid_when_roi_has_no_intersection(self) -> None:
        frame = FrameData(
            data=_mono8_frame_bytes([[0, 0, 255], [0, 0, 255], [0, 0, 255]]),
            metadata=FrameMetadata(width=3, height=3, pixel_format="Mono8", frame_id=45),
        )
        roi = RoiDefinition(
            roi_id="missing-roi",
            shape="rectangle",
            points=((10.0, 10.0), (12.0, 10.0), (12.0, 12.0), (10.0, 12.0)),
        )

        result = analyze_edge_profile(
            frame,
            request=EdgeProfileRequest(orientation="vertical", roi=roi),
        )

        self.assertFalse(result.is_valid)
        self.assertIsNone(result.dominant_edge_index)
        self.assertEqual(result.roi_id, "missing-roi")


if __name__ == "__main__":
    unittest.main()
