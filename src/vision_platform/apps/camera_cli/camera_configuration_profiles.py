from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vision_platform.models import ApplyConfigurationRequest


DEFAULT_CONFIGURATION_PROFILE_PATH = Path(__file__).resolve().parents[4] / "configs" / "camera_configuration_profiles.json"

_CONFIGURATION_FIELDS = (
    "exposure_time_us",
    "gain",
    "pixel_format",
    "acquisition_frame_rate",
    "roi_offset_x",
    "roi_offset_y",
    "roi_width",
    "roi_height",
)


@dataclass(slots=True)
class ResolvedCameraConfigurationProfile:
    profile_id: str
    camera_class: str
    configuration: ApplyConfigurationRequest


@dataclass(slots=True)
class CameraConfigurationProfileResolutionError(Exception):
    message: str
    details: dict[str, Any]

    def __str__(self) -> str:
        return self.message


def normalize_camera_class_name(camera_model: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", camera_model.strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized


def resolve_camera_configuration_profile(
    *,
    profile_id: str,
    camera_class: str,
    config_path: Path = DEFAULT_CONFIGURATION_PROFILE_PATH,
) -> ResolvedCameraConfigurationProfile:
    if not profile_id.strip():
        raise CameraConfigurationProfileResolutionError(
            message="Configuration profile id must not be empty.",
            details={"profile_id": profile_id, "config_path": str(config_path)},
        )
    if not camera_class.strip():
        raise CameraConfigurationProfileResolutionError(
            message="Camera class must not be empty when resolving a configuration profile.",
            details={"profile_id": profile_id, "camera_class": camera_class, "config_path": str(config_path)},
        )

    payload = _load_profile_payload(config_path)
    classes = payload.get("camera_classes")
    if not isinstance(classes, dict):
        raise CameraConfigurationProfileResolutionError(
            message="Configuration profile file is missing the 'camera_classes' mapping.",
            details={"config_path": str(config_path)},
        )

    class_payload = classes.get(camera_class)
    if not isinstance(class_payload, dict):
        raise CameraConfigurationProfileResolutionError(
            message=f"Configuration profile camera class '{camera_class}' is not defined.",
            details={
                "profile_id": profile_id,
                "camera_class": camera_class,
                "config_path": str(config_path),
            },
        )

    configuration_payload = class_payload.get(profile_id)
    if not isinstance(configuration_payload, dict):
        raise CameraConfigurationProfileResolutionError(
            message=f"Configuration profile '{profile_id}' is not defined for camera class '{camera_class}'.",
            details={
                "profile_id": profile_id,
                "camera_class": camera_class,
                "config_path": str(config_path),
            },
        )

    return ResolvedCameraConfigurationProfile(
        profile_id=profile_id,
        camera_class=camera_class,
        configuration=_build_apply_configuration_request(configuration_payload),
    )


def merge_configuration_requests(
    base: ApplyConfigurationRequest,
    overrides: ApplyConfigurationRequest,
) -> ApplyConfigurationRequest:
    merged: dict[str, Any] = {}
    for field_name in _CONFIGURATION_FIELDS:
        override_value = getattr(overrides, field_name)
        merged[field_name] = override_value if override_value is not None else getattr(base, field_name)
    return ApplyConfigurationRequest(**merged)


def has_configuration_values(request: ApplyConfigurationRequest) -> bool:
    return any(getattr(request, field_name) is not None for field_name in _CONFIGURATION_FIELDS)


def _load_profile_payload(config_path: Path) -> dict[str, Any]:
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CameraConfigurationProfileResolutionError(
            message=f"Configuration profile file was not found: {config_path}",
            details={"config_path": str(config_path)},
        ) from exc
    except json.JSONDecodeError as exc:
        raise CameraConfigurationProfileResolutionError(
            message=f"Configuration profile file is not valid JSON: {config_path}",
            details={"config_path": str(config_path), "error": str(exc)},
        ) from exc


def _build_apply_configuration_request(payload: dict[str, Any]) -> ApplyConfigurationRequest:
    unexpected_fields = sorted(set(payload) - set(_CONFIGURATION_FIELDS))
    if unexpected_fields:
        raise CameraConfigurationProfileResolutionError(
            message="Configuration profile contains unsupported fields.",
            details={"unsupported_fields": unexpected_fields},
        )
    return ApplyConfigurationRequest(**payload)


__all__ = [
    "CameraConfigurationProfileResolutionError",
    "DEFAULT_CONFIGURATION_PROFILE_PATH",
    "ResolvedCameraConfigurationProfile",
    "has_configuration_values",
    "merge_configuration_requests",
    "normalize_camera_class_name",
    "resolve_camera_configuration_profile",
]
