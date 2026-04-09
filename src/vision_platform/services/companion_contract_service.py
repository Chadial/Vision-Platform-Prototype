from __future__ import annotations

from typing import Any


def build_companion_command_result(
    *,
    command_name: str,
    result: Any,
    reflection_kind: str | None,
    reflection: dict[str, object | None] | None,
    failure_reflection: dict[str, object | None] | None,
) -> dict[str, Any]:
    return {
        "command": command_name,
        "reflection_kind": reflection_kind,
        "reflection": reflection,
        "failure_reflection": failure_reflection,
        "result": result,
    }


def build_failed_companion_command_result(
    *,
    command_name: str,
    failure_reflection: dict[str, object | None] | None,
) -> dict[str, Any]:
    return build_companion_command_result(
        command_name=command_name,
        result=None,
        reflection_kind=None,
        reflection=None,
        failure_reflection=failure_reflection,
    )


def build_companion_status_snapshot(
    *,
    session_id: str,
    source: str,
    camera_id: str | None,
    configuration_profile_id: str | None,
    focus_summary: str | None,
    setup_reflection: dict[str, object | None],
    failure_reflection: dict[str, object | None] | None,
    snapshot_reflection: dict[str, object | None],
    recording_summary: str | None,
    recording_reflection: dict[str, object | None],
    status_lines: list[str],
    status: Any,
) -> dict[str, Any]:
    return {
        "session_id": session_id,
        "source": source,
        "camera_id": camera_id,
        "configuration_profile_id": configuration_profile_id,
        "focus_summary": focus_summary,
        "setup_reflection": setup_reflection,
        "failure_reflection": failure_reflection,
        "snapshot_reflection": snapshot_reflection,
        "recording_summary": recording_summary,
        "recording_reflection": recording_reflection,
        "status_lines": status_lines,
        "status": status,
    }


__all__ = [
    "build_companion_command_result",
    "build_companion_status_snapshot",
    "build_failed_companion_command_result",
]
