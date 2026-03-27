from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vision_platform.integrations.camera.capability_probe import DEFAULT_FEATURE_NAMES, probe_camera_capabilities
from vision_platform.models import CameraCapabilityProfile, FeatureCapability


class CameraCapabilityService:
    """Normalizes live or stored camera capability data for validation and UI use."""

    def probe_live(
        self,
        camera_id: str | None = None,
        feature_names: tuple[str, ...] = DEFAULT_FEATURE_NAMES,
    ) -> CameraCapabilityProfile:
        return self.from_probe_payload(probe_camera_capabilities(camera_id=camera_id, feature_names=feature_names))

    def load_json(self, path: Path) -> CameraCapabilityProfile:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return self.from_probe_payload(payload)

    def from_probe_payload(self, payload: dict[str, Any]) -> CameraCapabilityProfile:
        camera = payload["camera"]
        features = {
            name: self._normalize_feature(name, feature_payload)
            for name, feature_payload in payload.get("features", {}).items()
        }
        return CameraCapabilityProfile(
            probe_utc=payload.get("probe_utc"),
            camera_id=str(camera.get("camera_id", "")),
            camera_name=str(camera.get("name", "")),
            camera_model=str(camera.get("model", "")),
            camera_serial=self._optional_str(camera.get("serial")),
            interface_id=self._optional_str(camera.get("interface_id")),
            feature_count=int(payload.get("feature_count", len(features))),
            software=dict(payload.get("software", {})),
            features=features,
        )

    @staticmethod
    def _normalize_feature(name: str, payload: dict[str, Any]) -> FeatureCapability:
        numeric_range = payload.get("range")
        minimum = None
        maximum = None
        if isinstance(numeric_range, list | tuple) and len(numeric_range) == 2:
            minimum = numeric_range[0]
            maximum = numeric_range[1]

        entries = payload.get("entries") or ()
        return FeatureCapability(
            name=name,
            feature_type=str(payload.get("type", "Unknown")),
            is_readable=payload.get("is_readable"),
            is_writeable=payload.get("is_writeable"),
            value=payload.get("value"),
            minimum=minimum,
            maximum=maximum,
            increment=payload.get("increment"),
            entries=tuple(str(entry) for entry in entries),
            missing=bool(payload.get("missing", False)),
            error=payload.get("error") or payload.get("value_error"),
        )

    @staticmethod
    def _optional_str(value: Any) -> str | None:
        if value is None:
            return None
        return str(value)


__all__ = ["CameraCapabilityService"]
