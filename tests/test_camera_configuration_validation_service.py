import unittest

from tests import _path_setup
from vision_platform.models import CameraCapabilityProfile, CameraConfiguration, FeatureCapability
from vision_platform.services import CameraConfigurationValidationService


class CameraConfigurationValidationServiceTests(unittest.TestCase):
    def test_validate_rejects_value_outside_numeric_range(self) -> None:
        service = CameraConfigurationValidationService()
        profile = self._build_profile(
            ExposureTime=FeatureCapability(
                name="ExposureTime",
                feature_type="FloatFeature",
                is_writeable=True,
                minimum=50.0,
                maximum=1000.0,
            )
        )

        with self.assertRaisesRegex(ValueError, "exposure_time_us"):
            service.validate(CameraConfiguration(exposure_time_us=10.0), profile)

    def test_validate_rejects_value_with_invalid_increment(self) -> None:
        service = CameraConfigurationValidationService()
        profile = self._build_profile(
            Width=FeatureCapability(
                name="Width",
                feature_type="IntFeature",
                is_writeable=True,
                minimum=8,
                maximum=4024,
                increment=8,
            )
        )

        with self.assertRaisesRegex(
            ValueError,
            r"roi_width=15.*increment 8.*base 8.*allowed range 8\.\.4024.*nearest valid values: 8, 16",
        ):
            service.validate(CameraConfiguration(roi_width=15), profile)

    def test_validate_rejects_value_outside_numeric_range_with_nearest_valid_value(self) -> None:
        service = CameraConfigurationValidationService()
        profile = self._build_profile(
            OffsetX=FeatureCapability(
                name="OffsetX",
                feature_type="IntFeature",
                is_writeable=True,
                minimum=0,
                maximum=16,
                increment=2,
            )
        )

        with self.assertRaisesRegex(
            ValueError,
            r"roi_offset_x=17.*<= 16.*allowed range 0\.\.16.*required increment 2 from base 0.*nearest valid values: 16",
        ):
            service.validate(CameraConfiguration(roi_offset_x=17), profile)

    def test_validate_rejects_enum_value_not_supported_by_camera(self) -> None:
        service = CameraConfigurationValidationService()
        profile = self._build_profile(
            PixelFormat=FeatureCapability(
                name="PixelFormat",
                feature_type="EnumFeature",
                is_writeable=True,
                entries=("Mono8", "Mono10"),
            )
        )

        with self.assertRaisesRegex(ValueError, "PixelFormat"):
            service.validate(CameraConfiguration(pixel_format="Mono16"), profile)

    def test_validate_allows_acquisition_frame_rate_when_enable_feature_is_writeable(self) -> None:
        service = CameraConfigurationValidationService()
        profile = self._build_profile(
            AcquisitionFrameRate=FeatureCapability(
                name="AcquisitionFrameRate",
                feature_type="FloatFeature",
                is_writeable=False,
                minimum=0.5,
                maximum=15.0,
            ),
            AcquisitionFrameRateEnable=FeatureCapability(
                name="AcquisitionFrameRateEnable",
                feature_type="BoolFeature",
                is_writeable=True,
            ),
        )

        service.validate(CameraConfiguration(acquisition_frame_rate=5.0), profile)

    def test_validate_rejects_unwriteable_feature_without_enable_path(self) -> None:
        service = CameraConfigurationValidationService()
        profile = self._build_profile(
            Gain=FeatureCapability(
                name="Gain",
                feature_type="FloatFeature",
                is_writeable=False,
                minimum=0.0,
                maximum=10.0,
            )
        )

        with self.assertRaisesRegex(ValueError, "not writeable"):
            service.validate(CameraConfiguration(gain=3.0), profile)

    @staticmethod
    def _build_profile(**features: FeatureCapability) -> CameraCapabilityProfile:
        return CameraCapabilityProfile(
            probe_utc=None,
            camera_id="CAM-001",
            camera_name="TestCam",
            camera_model="ModelA",
            camera_serial=None,
            interface_id=None,
            feature_count=len(features),
            features=dict(features),
        )


if __name__ == "__main__":
    unittest.main()
