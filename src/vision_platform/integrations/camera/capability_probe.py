from __future__ import annotations

from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path
from typing import Any

from vmbpy import VmbSystem


DEFAULT_FEATURE_NAMES = (
    "DeviceVendorName",
    "DeviceManufacturerInfo",
    "DeviceFamilyName",
    "DeviceModelName",
    "DeviceSerialNumber",
    "DeviceFirmwareVersion",
    "DeviceVersion",
    "DeviceTLVersionMajor",
    "DeviceTLVersionMinor",
    "DeviceSFNCVersionMajor",
    "DeviceSFNCVersionMinor",
    "DeviceSFNCVersionSubMinor",
    "DeviceLinkSpeed",
    "DeviceLinkThroughputLimit",
    "DeviceLinkThroughputLimitMode",
    "SensorWidth",
    "SensorHeight",
    "SensorBitDepth",
    "PixelSize",
    "PixelFormat",
    "ExposureTime",
    "ExposureAuto",
    "ExposureMode",
    "Gain",
    "GainAuto",
    "AcquisitionMode",
    "AcquisitionFrameRateEnable",
    "AcquisitionFrameRate",
    "AcquisitionFrameRateMode",
    "TriggerMode",
    "TriggerSource",
    "TriggerSelector",
    "LineSelector",
    "LineMode",
    "LineSource",
    "UserSetSelector",
    "UserSetDefault",
    "BinningHorizontal",
    "BinningVertical",
    "ReverseX",
    "ReverseY",
    "ChunkModeActive",
    "ChunkSelector",
    "TimerSelector",
    "CounterSelector",
    "Width",
    "Height",
    "OffsetX",
    "OffsetY",
)


def _package_version(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def _normalize_scalar(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_normalize_scalar(item) for item in value]
    if isinstance(value, list):
        return [_normalize_scalar(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _serialize_feature(feature) -> dict[str, Any]:
    item: dict[str, Any] = {"type": type(feature).__name__}
    for attr in ("is_readable", "is_writeable"):
        method = getattr(feature, attr, None)
        if callable(method):
            item[attr] = bool(method())

    getter = getattr(feature, "get", None)
    if callable(getter):
        try:
            item["value"] = _normalize_scalar(getter())
        except Exception as exc:
            item["value_error"] = str(exc)

    range_getter = getattr(feature, "get_range", None)
    if callable(range_getter):
        try:
            item["range"] = _normalize_scalar(range_getter())
        except Exception as exc:
            item["range_error"] = str(exc)

    increment_getter = getattr(feature, "get_increment", None)
    if callable(increment_getter):
        try:
            item["increment"] = _normalize_scalar(increment_getter())
        except Exception as exc:
            item["increment_error"] = str(exc)

    entries_getter = getattr(feature, "get_available_entries", None)
    if callable(entries_getter):
        try:
            item["entries"] = [str(entry) for entry in entries_getter()]
        except Exception as exc:
            item["entries_error"] = str(exc)

    return item


def _serialize_camera_payload(camera, feature_names: tuple[str, ...]) -> dict[str, Any]:
    all_features = camera.get_all_features()
    features: dict[str, Any] = {}
    for feature_name in feature_names:
        try:
            features[feature_name] = _serialize_feature(camera.get_feature_by_name(feature_name))
        except Exception as exc:
            features[feature_name] = {"missing": True, "error": str(exc)}

    return {
        "probe_utc": datetime.now(timezone.utc).isoformat(),
        "camera": {
            "camera_id": camera.get_id(),
            "name": camera.get_name(),
            "model": camera.get_model(),
            "serial": camera.get_serial(),
            "interface_id": camera.get_interface_id(),
        },
        "software": {
            "vmbpy_version": _package_version("vmbpy"),
        },
        "feature_count": len(all_features),
        "features": features,
    }


def probe_open_camera_capabilities(
    camera,
    feature_names: tuple[str, ...] = DEFAULT_FEATURE_NAMES,
) -> dict[str, Any]:
    return _serialize_camera_payload(camera, feature_names=feature_names)


def probe_camera_capabilities(
    camera_id: str | None = None,
    feature_names: tuple[str, ...] = DEFAULT_FEATURE_NAMES,
) -> dict[str, Any]:
    with VmbSystem.get_instance() as vmb:
        camera = vmb.get_camera_by_id(camera_id) if camera_id else vmb.get_all_cameras()[0]
        with camera:
            return _serialize_camera_payload(camera, feature_names=feature_names)


def write_camera_capabilities_json(
    output_path: Path,
    camera_id: str | None = None,
    feature_names: tuple[str, ...] = DEFAULT_FEATURE_NAMES,
) -> Path:
    payload = probe_camera_capabilities(camera_id=camera_id, feature_names=feature_names)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


__all__ = [
    "DEFAULT_FEATURE_NAMES",
    "probe_camera_capabilities",
    "probe_open_camera_capabilities",
    "write_camera_capabilities_json",
]
