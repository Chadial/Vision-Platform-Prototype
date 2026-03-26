from datetime import datetime, timezone
import unittest

from vision_platform.libraries.common_models import FocusRequest, FrameData, FrameMetadata, RoiDefinition
from vision_platform.libraries.focus_core import LaplaceFocusEvaluator, evaluate_focus, focus_score_available
from vision_platform.models import CapturedFrame


def _mono8_frame_bytes(rows: list[list[int]]) -> bytes:
    return bytes(value for row in rows for value in row)


class FocusCoreTests(unittest.TestCase):
    def test_laplace_score_prefers_structured_image_over_flat_image(self) -> None:
        evaluator = LaplaceFocusEvaluator()
        flat_frame = FrameData(
            data=_mono8_frame_bytes([[32] * 5 for _ in range(5)]),
            metadata=FrameMetadata(width=5, height=5, pixel_format="Mono8", frame_id=1),
        )
        structured_frame = FrameData(
            data=_mono8_frame_bytes(
                [
                    [0, 255, 0, 255, 0],
                    [255, 0, 255, 0, 255],
                    [0, 255, 0, 255, 0],
                    [255, 0, 255, 0, 255],
                    [0, 255, 0, 255, 0],
                ]
            ),
            metadata=FrameMetadata(width=5, height=5, pixel_format="Mono8", frame_id=2),
        )

        flat_result = evaluator.evaluate(flat_frame)
        structured_result = evaluator.evaluate(structured_frame)

        self.assertTrue(flat_result.is_valid)
        self.assertTrue(structured_result.is_valid)
        self.assertLess(flat_result.score, structured_result.score)

    def test_evaluate_focus_accepts_captured_frame_input(self) -> None:
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
            frame_id=7,
            pixel_format="Mono8",
            timestamp_utc=datetime.now(timezone.utc),
        )

        result = evaluate_focus(frame)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.source_frame_id, 7)
        self.assertEqual(result.metric_name, "laplace_variance")
        self.assertGreater(result.score, 0.0)

    def test_roi_can_focus_on_a_structured_subregion(self) -> None:
        evaluator = LaplaceFocusEvaluator()
        frame = FrameData(
            data=_mono8_frame_bytes(
                [
                    [16, 16, 16, 16, 16, 16],
                    [16, 16, 16, 0, 255, 0],
                    [16, 16, 16, 255, 0, 255],
                    [16, 16, 16, 0, 255, 0],
                    [16, 16, 16, 255, 0, 255],
                    [16, 16, 16, 0, 255, 0],
                ]
            ),
            metadata=FrameMetadata(width=6, height=6, pixel_format="Mono8", frame_id=8),
        )
        request = FocusRequest(
            method="laplace",
            roi=RoiDefinition(
                roi_id="focus-zone",
                shape="rectangle",
                points=((3.0, 1.0), (6.0, 6.0)),
            ),
        )

        result = evaluator.evaluate(frame, request=request)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.roi_id, "focus-zone")
        self.assertGreater(result.score, 0.0)

    def test_too_small_frames_are_reported_as_invalid(self) -> None:
        frame = FrameData(
            data=_mono8_frame_bytes([[0, 255], [255, 0]]),
            metadata=FrameMetadata(width=2, height=2, pixel_format="Mono8"),
        )

        result = evaluate_focus(frame)

        self.assertFalse(focus_score_available(frame, FocusRequest(method="laplace")))
        self.assertFalse(result.is_valid)
        self.assertEqual(result.score, 0.0)

    def test_disabled_roi_falls_back_to_whole_frame_scoring(self) -> None:
        frame = FrameData(
            data=_mono8_frame_bytes(
                [
                    [0, 255, 0, 255, 0],
                    [255, 0, 255, 0, 255],
                    [0, 255, 0, 255, 0],
                    [255, 0, 255, 0, 255],
                    [0, 255, 0, 255, 0],
                ]
            ),
            metadata=FrameMetadata(width=5, height=5, pixel_format="Mono8", frame_id=9),
        )
        disabled_roi_request = FocusRequest(
            method="laplace",
            roi=RoiDefinition(
                roi_id="ignored-roi",
                shape="rectangle",
                points=((1.0, 1.0), (4.0, 4.0)),
                enabled=False,
            ),
        )

        full_result = evaluate_focus(frame)
        disabled_roi_result = evaluate_focus(frame, request=disabled_roi_request)

        self.assertTrue(disabled_roi_result.is_valid)
        self.assertEqual(full_result.score, disabled_roi_result.score)


if __name__ == "__main__":
    unittest.main()
