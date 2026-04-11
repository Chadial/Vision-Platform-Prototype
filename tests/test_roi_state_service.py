import unittest

from tests import _path_setup
from vision_platform.libraries.common_models import RoiDefinition
from vision_platform.services.stream_service import RoiStateService


class RoiStateServiceTests(unittest.TestCase):
    def test_resolve_active_roi_returns_explicit_roi_when_provided(self) -> None:
        service = RoiStateService()
        service.set_active_roi(
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

        resolved_roi = service.resolve_active_roi(explicit_roi)

        self.assertIs(resolved_roi, explicit_roi)

    def test_resolve_active_roi_returns_shared_active_roi_when_explicit_is_missing(self) -> None:
        service = RoiStateService()
        shared_roi = RoiDefinition(
            roi_id="state-roi",
            shape="rectangle",
            points=((1.0, 1.0), (5.0, 1.0), (5.0, 5.0), (1.0, 5.0)),
        )
        service.set_active_roi(shared_roi)

        resolved_roi = service.resolve_active_roi()

        self.assertIs(resolved_roi, shared_roi)

    def test_resolve_active_roi_returns_none_without_explicit_or_shared_roi(self) -> None:
        service = RoiStateService()

        resolved_roi = service.resolve_active_roi()

        self.assertIsNone(resolved_roi)

    def test_clear_active_roi_preserves_stored_shape_in_inactive_state(self) -> None:
        service = RoiStateService()
        shared_roi = RoiDefinition(
            roi_id="state-roi",
            shape="rectangle",
            points=((1.0, 1.0), (5.0, 1.0), (5.0, 5.0), (1.0, 5.0)),
        )
        service.set_active_roi(shared_roi)

        service.clear_active_roi()

        self.assertIsNone(service.get_active_roi())
        stored_roi = service.get_roi("rectangle")
        self.assertIsNotNone(stored_roi)
        self.assertFalse(stored_roi.enabled)
        self.assertEqual(stored_roi.points, shared_roi.points)

    def test_set_active_roi_switches_active_shape_exclusively(self) -> None:
        service = RoiStateService()
        rectangle_roi = RoiDefinition(
            roi_id="rect",
            shape="rectangle",
            points=((1.0, 1.0), (5.0, 1.0), (5.0, 5.0), (1.0, 5.0)),
        )
        ellipse_roi = RoiDefinition(
            roi_id="ellipse",
            shape="ellipse",
            points=((2.0, 2.0), (6.0, 2.0), (6.0, 6.0), (2.0, 6.0)),
        )
        service.set_active_roi(rectangle_roi)
        service.set_active_roi(ellipse_roi)

        self.assertEqual(service.get_active_roi(), ellipse_roi)
        self.assertTrue(service.get_roi("ellipse").enabled)
        self.assertFalse(service.get_roi("rectangle").enabled)
        self.assertEqual(service.get_active_roi_shape(), "ellipse")


if __name__ == "__main__":
    unittest.main()
