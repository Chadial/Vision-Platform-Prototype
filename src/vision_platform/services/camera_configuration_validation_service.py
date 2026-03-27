from __future__ import annotations

import math

from vision_platform.models import CameraCapabilityProfile, CameraConfiguration, FeatureCapability


class CameraConfigurationValidationService:
    """Validates camera configuration values against a capability profile."""

    _FIELD_TO_FEATURE = {
        "exposure_time_us": "ExposureTime",
        "gain": "Gain",
        "pixel_format": "PixelFormat",
        "acquisition_frame_rate": "AcquisitionFrameRate",
        "roi_offset_x": "OffsetX",
        "roi_offset_y": "OffsetY",
        "roi_width": "Width",
        "roi_height": "Height",
    }

    def validate(
        self,
        config: CameraConfiguration,
        capability_profile: CameraCapabilityProfile | None,
    ) -> None:
        if capability_profile is None:
            return

        for field_name, feature_name in self._FIELD_TO_FEATURE.items():
            value = getattr(config, field_name)
            if value is None:
                continue
            feature = capability_profile.get_feature(feature_name)
            if feature is None:
                continue
            self._validate_field(
                field_name=field_name,
                value=value,
                feature=feature,
                capability_profile=capability_profile,
            )

    def _validate_field(
        self,
        field_name: str,
        value: float | int | str,
        feature: FeatureCapability,
        capability_profile: CameraCapabilityProfile,
    ) -> None:
        if feature.missing:
            raise ValueError(
                f"CameraConfiguration.{field_name} is not supported by camera feature '{feature.name}'."
            )

        if not self._is_feature_writeable(feature, capability_profile):
            raise ValueError(
                f"CameraConfiguration.{field_name} cannot be applied because camera feature '{feature.name}' "
                "is not writeable in the current capability profile."
            )

        if feature.is_enum:
            self._validate_enum(field_name, str(value), feature)
            return

        if isinstance(value, bool):
            return

        if isinstance(value, int | float):
            self._validate_numeric(field_name, value, feature)

    @staticmethod
    def _validate_enum(field_name: str, value: str, feature: FeatureCapability) -> None:
        if value not in feature.entries:
            choices = ", ".join(feature.entries)
            raise ValueError(
                f"CameraConfiguration.{field_name} must be one of [{choices}] for camera feature '{feature.name}'."
            )

    def _validate_numeric(self, field_name: str, value: int | float, feature: FeatureCapability) -> None:
        if feature.minimum is not None and value < feature.minimum:
            raise ValueError(
                f"CameraConfiguration.{field_name} must be >= {feature.minimum} for camera feature '{feature.name}'."
            )
        if feature.maximum is not None and value > feature.maximum:
            raise ValueError(
                f"CameraConfiguration.{field_name} must be <= {feature.maximum} for camera feature '{feature.name}'."
            )
        if feature.increment in (None, 0):
            return

        base = feature.minimum if feature.minimum is not None else 0
        if isinstance(value, int) and isinstance(base, int) and isinstance(feature.increment, int):
            if (value - base) % feature.increment != 0:
                raise ValueError(
                    f"CameraConfiguration.{field_name} must align to increment {feature.increment} "
                    f"from base {base} for camera feature '{feature.name}'."
                )
            return

        step_count = (float(value) - float(base)) / float(feature.increment)
        if not math.isclose(step_count, round(step_count), rel_tol=1e-9, abs_tol=1e-6):
            raise ValueError(
                f"CameraConfiguration.{field_name} must align to increment {feature.increment} "
                f"from base {base} for camera feature '{feature.name}'."
            )

    @staticmethod
    def _is_feature_writeable(
        feature: FeatureCapability,
        capability_profile: CameraCapabilityProfile,
    ) -> bool:
        if feature.is_writeable:
            return True
        if feature.name != "AcquisitionFrameRate":
            return False

        enable_feature = capability_profile.get_feature("AcquisitionFrameRateEnable")
        return bool(enable_feature and not enable_feature.missing and enable_feature.is_writeable)


__all__ = ["CameraConfigurationValidationService"]
