import unittest

from vision_platform.libraries.common_models import RoiDefinition
from vision_platform.libraries.roi_core import roi_bounds, roi_centroid, roi_mask, roi_pixel_bounds


class RoiCoreTests(unittest.TestCase):
    def test_roi_pixel_bounds_floor_ceil_and_clamp_to_frame(self) -> None:
        roi = RoiDefinition(
            roi_id="roi-1",
            shape="rectangle",
            points=((-2.2, 1.2), (5.8, 6.1)),
        )

        bounds = roi_pixel_bounds(roi, width=5, height=4)

        self.assertEqual((0, 1, 5, 4), bounds)

    def test_rectangle_roi_mask_fills_the_cropped_window(self) -> None:
        roi = RoiDefinition(
            roi_id="roi-2",
            shape="rectangle",
            points=((1.0, 1.0), (4.0, 4.0)),
        )

        masked_roi = roi_mask(roi, width=6, height=6)

        self.assertIsNotNone(masked_roi)
        bounds, mask = masked_roi or ((0, 0, 0, 0), [])
        self.assertEqual((1, 1, 4, 4), bounds)
        self.assertEqual(
            [
                [True, True, True],
                [True, True, True],
                [True, True, True],
            ],
            mask,
        )

    def test_ellipse_roi_mask_marks_only_pixels_inside_the_shape(self) -> None:
        roi = RoiDefinition(
            roi_id="roi-3",
            shape="ellipse",
            points=((1.0, 1.0), (5.0, 5.0)),
        )

        masked_roi = roi_mask(roi, width=8, height=8)

        self.assertIsNotNone(masked_roi)
        bounds, mask = masked_roi or ((0, 0, 0, 0), [])
        self.assertEqual((1, 1, 5, 5), bounds)
        self.assertEqual(
            [
                [False, True, True, False],
                [True, True, True, True],
                [True, True, True, True],
                [False, True, True, False],
            ],
            mask,
        )

    def test_existing_float_bounds_and_centroid_helpers_remain_portable(self) -> None:
        roi = RoiDefinition(
            roi_id="roi-4",
            shape="rectangle",
            points=((1.0, 2.0), (5.0, 7.0)),
        )

        self.assertEqual((1.0, 2.0, 5.0, 7.0), roi_bounds(roi))
        self.assertEqual((3.0, 4.5), roi_centroid(roi))


if __name__ == "__main__":
    unittest.main()
