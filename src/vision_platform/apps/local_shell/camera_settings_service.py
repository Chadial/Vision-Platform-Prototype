from __future__ import annotations

import math
from dataclasses import dataclass

from vision_platform.apps.camera_cli.camera_configuration_profiles import (
    CameraConfigurationProfileResolutionError,
    merge_configuration_requests,
    normalize_camera_class_name,
    resolve_camera_configuration_profile,
)
from vision_platform.models import ApplyConfigurationRequest, CameraCapabilityProfile, CameraConfiguration, FeatureCapability

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


@dataclass(frozen=True, slots=True)
class CameraSettingsFieldHint:
    tooltip: str | None = None


class CameraSettingsService:
    def build_initial_request(
        self,
        *,
        current_configuration: CameraConfiguration | None,
        profile_id: str | None,
        camera_class: str | None,
        capability_profile: CameraCapabilityProfile | None,
    ) -> ApplyConfigurationRequest:
        base_request = (
            ApplyConfigurationRequest.from_camera_configuration(current_configuration)
            if current_configuration is not None
            else ApplyConfigurationRequest()
        )
        resolved_profile = self._resolve_profile_request(profile_id=profile_id, camera_class=camera_class)
        if resolved_profile is not None:
            base_request = merge_configuration_requests(base_request, resolved_profile)
        return self.normalize_request(base_request, capability_profile)

    def build_field_hints(
        self,
        capability_profile: CameraCapabilityProfile | None,
    ) -> dict[str, CameraSettingsFieldHint]:
        if capability_profile is None:
            return {}
        hints: dict[str, CameraSettingsFieldHint] = {}
        for field_name, feature_name in _FIELD_TO_FEATURE.items():
            feature = capability_profile.get_feature(feature_name)
            if feature is None:
                continue
            tooltip = self._format_feature_hint(feature)
            if tooltip:
                hints[field_name] = CameraSettingsFieldHint(tooltip=tooltip)
        return hints

    def normalize_request(
        self,
        request: ApplyConfigurationRequest,
        capability_profile: CameraCapabilityProfile | None,
    ) -> ApplyConfigurationRequest:
        if capability_profile is None:
            return request
        normalized = {}
        for field_name, feature_name in _FIELD_TO_FEATURE.items():
            value = getattr(request, field_name)
            feature = capability_profile.get_feature(feature_name)
            normalized[field_name] = self._normalize_value(value, feature)
        return ApplyConfigurationRequest(**normalized)

    def _resolve_profile_request(
        self,
        *,
        profile_id: str | None,
        camera_class: str | None,
    ) -> ApplyConfigurationRequest | None:
        if camera_class is None:
            return None
        resolved_profile_id = (profile_id or "default").strip()
        resolved_camera_class = camera_class.strip()
        if not resolved_profile_id or not resolved_camera_class:
            return None
        try:
            resolved = resolve_camera_configuration_profile(
                profile_id=resolved_profile_id,
                camera_class=resolved_camera_class,
            )
        except CameraConfigurationProfileResolutionError:
            if profile_id is None:
                try:
                    resolved = resolve_camera_configuration_profile(
                        profile_id="default",
                        camera_class=normalize_camera_class_name(resolved_camera_class),
                    )
                except CameraConfigurationProfileResolutionError:
                    return None
            else:
                return None
        return resolved.configuration

    @staticmethod
    def _format_feature_hint(feature: FeatureCapability) -> str | None:
        if feature.missing:
            return None
        if feature.is_enum and feature.entries:
            return f"Allowed values: {', '.join(feature.entries)}"
        if feature.minimum is None and feature.maximum is None and feature.increment in (None, 0):
            return None
        parts: list[str] = []
        if feature.minimum is not None or feature.maximum is not None:
            parts.append(
                f"Range: {CameraSettingsService._format_number(feature.minimum)}..{CameraSettingsService._format_number(feature.maximum)}"
            )
        if feature.increment not in (None, 0):
            parts.append(f"Step: {CameraSettingsService._format_number(feature.increment)}")
        return ", ".join(parts) if parts else None

    @staticmethod
    def _normalize_value(
        value: float | int | str | None,
        feature: FeatureCapability | None,
    ) -> float | int | str | None:
        if value is None or feature is None or feature.missing:
            return value
        if feature.is_enum:
            text_value = str(value)
            if text_value in feature.entries or not feature.entries:
                return text_value
            return feature.entries[0]
        if isinstance(value, str):
            return value
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return CameraSettingsService._normalize_numeric_value(value, feature)
        return value

    @staticmethod
    def _normalize_numeric_value(value: int | float, feature: FeatureCapability) -> int | float:
        normalized = float(value)
        if feature.minimum is not None:
            normalized = max(normalized, float(feature.minimum))
        if feature.maximum is not None:
            normalized = min(normalized, float(feature.maximum))
        increment = feature.increment
        if increment in (None, 0):
            return CameraSettingsService._normalize_numeric_type(normalized, feature, value)

        base = float(feature.minimum if feature.minimum is not None else 0)
        aligned = base + math.floor(((normalized - base) / float(increment)) + 0.5) * float(increment)
        if feature.minimum is not None:
            aligned = max(aligned, float(feature.minimum))
        if feature.maximum is not None:
            aligned = min(aligned, float(feature.maximum))
        return CameraSettingsService._normalize_numeric_type(aligned, feature, value)

    @staticmethod
    def _normalize_numeric_type(candidate: float, feature: FeatureCapability, requested_value: int | float) -> int | float:
        if all(isinstance(item, int) for item in (feature.minimum, feature.maximum, feature.increment, requested_value)):
            return int(round(candidate))
        return candidate

    @staticmethod
    def _format_number(value: int | float | None) -> str:
        if value is None:
            return "-"
        if isinstance(value, int):
            return str(value)
        if float(value).is_integer():
            return str(int(value))
        return f"{value:g}"


__all__ = ["CameraSettingsFieldHint", "CameraSettingsService"]
