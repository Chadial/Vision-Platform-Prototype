from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class FeatureCapability:
    name: str
    feature_type: str
    is_readable: bool | None = None
    is_writeable: bool | None = None
    value: Any | None = None
    minimum: float | int | None = None
    maximum: float | int | None = None
    increment: float | int | None = None
    entries: tuple[str, ...] = ()
    missing: bool = False
    error: str | None = None

    @property
    def is_numeric(self) -> bool:
        return self.minimum is not None or self.maximum is not None or self.increment is not None

    @property
    def is_enum(self) -> bool:
        return bool(self.entries)


@dataclass(frozen=True, slots=True)
class CameraCapabilityProfile:
    probe_utc: str | None
    camera_id: str
    camera_name: str
    camera_model: str
    camera_serial: str | None
    interface_id: str | None
    feature_count: int
    software: dict[str, Any] = field(default_factory=dict)
    features: dict[str, FeatureCapability] = field(default_factory=dict)

    def get_feature(self, name: str) -> FeatureCapability | None:
        return self.features.get(name)

    def require_feature(self, name: str) -> FeatureCapability:
        feature = self.get_feature(name)
        if feature is None:
            raise KeyError(f"Feature '{name}' is not present in this capability profile.")
        return feature


__all__ = ["CameraCapabilityProfile", "FeatureCapability"]
