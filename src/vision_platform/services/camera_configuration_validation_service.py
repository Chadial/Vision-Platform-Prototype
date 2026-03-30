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
                self._build_range_error_message(
                    field_name=field_name,
                    value=value,
                    feature=feature,
                    bound_kind="minimum",
                )
            )
        if feature.maximum is not None and value > feature.maximum:
            raise ValueError(
                self._build_range_error_message(
                    field_name=field_name,
                    value=value,
                    feature=feature,
                    bound_kind="maximum",
                )
            )
        if feature.increment in (None, 0):
            return

        base = feature.minimum if feature.minimum is not None else 0
        if isinstance(value, int) and isinstance(base, int) and isinstance(feature.increment, int):
            if (value - base) % feature.increment != 0:
                raise ValueError(self._build_increment_error_message(field_name, value, feature, base))
            return

        step_count = (float(value) - float(base)) / float(feature.increment)
        if not math.isclose(step_count, round(step_count), rel_tol=1e-9, abs_tol=1e-6):
            raise ValueError(self._build_increment_error_message(field_name, value, feature, base))

    def _build_range_error_message(
        self,
        *,
        field_name: str,
        value: int | float,
        feature: FeatureCapability,
        bound_kind: str,
    ) -> str:
        range_text = self._format_range(feature)
        nearest_text = self._format_nearest_valid_values(value, feature)
        comparator = ">=" if bound_kind == "minimum" else "<="
        bound_value = feature.minimum if bound_kind == "minimum" else feature.maximum
        message = (
            f"CameraConfiguration.{field_name}={value} is invalid for camera feature '{feature.name}': "
            f"value must be {comparator} {bound_value}"
        )
        if range_text is not None:
            message += f"; allowed range {range_text}"
        if feature.increment not in (None, 0):
            message += f"; required increment {feature.increment} from base {self._format_number(self._increment_base(feature))}"
        if nearest_text is not None:
            message += f"; nearest valid values: {nearest_text}"
        return message + "."

    def _build_increment_error_message(
        self,
        field_name: str,
        value: int | float,
        feature: FeatureCapability,
        base: int | float,
    ) -> str:
        range_text = self._format_range(feature)
        nearest_text = self._format_nearest_valid_values(value, feature)
        message = (
            f"CameraConfiguration.{field_name}={value} is invalid for camera feature '{feature.name}': "
            f"value must align to increment {feature.increment} from base {self._format_number(base)}"
        )
        if range_text is not None:
            message += f"; allowed range {range_text}"
        if nearest_text is not None:
            message += f"; nearest valid values: {nearest_text}"
        return message + "."

    @staticmethod
    def _increment_base(feature: FeatureCapability) -> int | float:
        return feature.minimum if feature.minimum is not None else 0

    def _format_nearest_valid_values(
        self,
        value: int | float,
        feature: FeatureCapability,
    ) -> str | None:
        increment = feature.increment
        if increment in (None, 0):
            return None

        base = float(self._increment_base(feature))
        increment_value = float(increment)
        step_count = (float(value) - base) / increment_value
        lower_step = math.floor(step_count)
        upper_step = math.ceil(step_count)
        candidates = []
        for step in (lower_step, upper_step):
            candidate = base + (step * increment_value)
            if feature.minimum is not None and candidate < float(feature.minimum):
                continue
            if feature.maximum is not None and candidate > float(feature.maximum):
                continue
            candidates.append(candidate)

        if not candidates:
            return None

        unique_candidates: list[int | float] = []
        for candidate in candidates:
            normalized = self._normalize_candidate(candidate, feature, value)
            if normalized not in unique_candidates:
                unique_candidates.append(normalized)

        return ", ".join(self._format_number(candidate) for candidate in unique_candidates)

    @staticmethod
    def _normalize_candidate(
        candidate: float,
        feature: FeatureCapability,
        requested_value: int | float,
    ) -> int | float:
        if all(isinstance(item, int) for item in (feature.minimum, feature.maximum, feature.increment, requested_value)):
            return int(round(candidate))
        return candidate

    @staticmethod
    def _format_range(feature: FeatureCapability) -> str | None:
        if feature.minimum is None and feature.maximum is None:
            return None
        minimum = "-inf" if feature.minimum is None else CameraConfigurationValidationService._format_number(feature.minimum)
        maximum = "inf" if feature.maximum is None else CameraConfigurationValidationService._format_number(feature.maximum)
        return f"{minimum}..{maximum}"

    @staticmethod
    def _format_number(value: int | float) -> str:
        if isinstance(value, int):
            return str(value)
        if float(value).is_integer():
            return str(int(value))
        return str(value)

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
