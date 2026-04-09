from __future__ import annotations

from typing import Any, Mapping


def build_labview_status_mapping(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    status = _as_mapping(snapshot.get("status"))
    camera = _as_mapping(status.get("camera"))
    setup_reflection = _as_mapping(snapshot.get("setup_reflection"))
    snapshot_reflection = _as_mapping(snapshot.get("snapshot_reflection"))
    recording_reflection = _as_mapping(snapshot.get("recording_reflection"))
    failure_reflection = _as_mapping(snapshot.get("failure_reflection"))

    return {
        "mapping_version": 1,
        "host_stage": "stage2_labview_candidate",
        "camera_ready": _as_bool(camera.get("is_initialized")),
        "camera_id": snapshot.get("camera_id"),
        "preview_running": _status_prefix_contains(snapshot.get("status_lines"), "preview=running"),
        "save_directory": status.get("default_save_directory"),
        "focus_value": snapshot.get("focus_summary"),
        "roi_enabled": _as_bool(setup_reflection.get("roi_active")),
        "roi_shape": setup_reflection.get("roi_shape"),
        "snapshot_phase": snapshot_reflection.get("phase"),
        "snapshot_file_name": snapshot_reflection.get("file_name"),
        "recording_phase": recording_reflection.get("phase"),
        "recording_file_stem": recording_reflection.get("file_stem"),
        "recording_save_directory": recording_reflection.get("save_directory"),
        "recording_stop_category": recording_reflection.get("stop_category"),
        "recording_frames_written": recording_reflection.get("frames_written"),
        "failure_source": failure_reflection.get("source"),
        "failure_message": failure_reflection.get("message"),
    }


def build_labview_command_mapping(command_result: Mapping[str, Any]) -> dict[str, Any]:
    nested_result = _as_mapping(command_result.get("result"))
    reflection = _as_mapping(nested_result.get("reflection"))
    failure_reflection = _as_mapping(nested_result.get("failure_reflection"))

    save_directory = reflection.get("save_directory")
    if save_directory is None:
        save_directory = reflection.get("selected_directory")

    return {
        "mapping_version": 1,
        "host_stage": "stage2_labview_candidate",
        "command_name": command_result.get("command_name") or nested_result.get("command"),
        "command_ok": _as_bool(command_result.get("success")),
        "reflection_kind": nested_result.get("reflection_kind"),
        "phase": reflection.get("phase"),
        "save_directory": save_directory,
        "file_name": reflection.get("file_name"),
        "file_stem": reflection.get("file_stem"),
        "frames_written": reflection.get("frames_written"),
        "stop_category": reflection.get("stop_category"),
        "failure_source": failure_reflection.get("source"),
        "failure_message": failure_reflection.get("message"),
    }


def attach_labview_mapping_to_status_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(snapshot)
    payload["labview_mapping"] = build_labview_status_mapping(snapshot)
    return payload


def attach_labview_mapping_to_command_result(command_result: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(command_result)
    payload["labview_mapping"] = build_labview_command_mapping(command_result)
    return payload


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _as_bool(value: Any) -> bool:
    return bool(value)


def _status_prefix_contains(status_lines: Any, token: str) -> bool:
    if not isinstance(status_lines, list) or not status_lines:
        return False
    first_line = status_lines[0]
    if not isinstance(first_line, str):
        return False
    return token in first_line


__all__ = [
    "attach_labview_mapping_to_command_result",
    "attach_labview_mapping_to_status_snapshot",
    "build_labview_command_mapping",
    "build_labview_status_mapping",
]
