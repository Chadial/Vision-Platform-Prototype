from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import TextIO

from vision_platform.models import CameraConfiguration, CapturedFrame, RecordingRequest, RecordingStatus, SnapshotRequest

_RECORDING_TRACE_LOG_STEM = "bounded_recording_traceability"
_RECORDING_TRACE_LOG_SUFFIX = ".csv"
_RECORDING_TRACE_ROW_HEADER = [
    "run_id",
    "image_name",
    "frame_id",
    "camera_timestamp",
    "system_timestamp_utc",
]


def build_snapshot_trace_path(saved_path: Path) -> Path:
    return saved_path.with_name(f"{saved_path.name}.trace.json")


def write_snapshot_trace_sidecar(
    saved_path: Path,
    request: SnapshotRequest,
    frame: CapturedFrame,
    configuration: CameraConfiguration | None,
) -> Path:
    trace_path = build_snapshot_trace_path(saved_path)
    record = {
        "record_kind": "snapshot_artifact",
        "saved_path": str(saved_path),
        "saved_file_name": saved_path.name,
        "system_timestamp_utc": frame.timestamp_utc.isoformat(),
        "camera_timestamp": frame.camera_timestamp,
        "camera_id": request.camera_id,
        "pixel_format": frame.pixel_format or _configuration_value(configuration, "pixel_format"),
        "exposure_time_us": _configuration_value(configuration, "exposure_time_us"),
        "gain": _configuration_value(configuration, "gain"),
    }
    _write_json_record(trace_path, record)
    return trace_path


def resolve_recording_trace_log_path(
    request: RecordingRequest,
    configuration: CameraConfiguration | None,
) -> tuple[Path, bool, dict[str, str]]:
    if request.save_directory is None:
        raise ValueError("RecordingRequest.save_directory must be set before resolving a traceability log.")

    stable_context = build_recording_stable_context(request, configuration)
    for candidate in _iter_recording_trace_candidates(request.save_directory):
        if candidate.exists() and _read_recording_stable_context(candidate) == stable_context:
            return candidate, True, stable_context

    candidate_paths = list(_iter_recording_trace_candidates(request.save_directory))
    for candidate in candidate_paths:
        if not candidate.exists():
            return candidate, False, stable_context
    raise RuntimeError("Unable to resolve a bounded recording traceability log path.")


def build_recording_stable_context(
    request: RecordingRequest,
    configuration: CameraConfiguration | None,
) -> dict[str, str]:
    return {
        "record_kind": "bounded_recording_folder_log",
        "save_directory": str(request.save_directory),
        "camera_id": _string_value(request.camera_id),
        "file_extension": _string_value(request.file_extension),
        "pixel_format": _string_value(_configuration_value(configuration, "pixel_format")),
        "exposure_time_us": _string_value(_configuration_value(configuration, "exposure_time_us")),
        "gain": _string_value(_configuration_value(configuration, "gain")),
        "roi_x": _string_value(_configuration_value(configuration, "roi_offset_x")),
        "roi_y": _string_value(_configuration_value(configuration, "roi_offset_y")),
        "roi_width": _string_value(_configuration_value(configuration, "roi_width")),
        "roi_height": _string_value(_configuration_value(configuration, "roi_height")),
    }


def open_recording_trace_log(
    path: Path,
    stable_context: dict[str, str],
    reused_existing_log: bool,
) -> tuple[TextIO, csv.writer]:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a", newline="", encoding="utf-8")
    writer = csv.writer(handle)
    if not reused_existing_log:
        for key, value in stable_context.items():
            handle.write(f"# context.{key}: {value}\n")
        writer.writerow(_RECORDING_TRACE_ROW_HEADER)
        handle.flush()
    return handle, writer


def append_recording_trace_run_start(
    handle: TextIO,
    run_id: str,
    request: RecordingRequest,
    session_start_utc: str | None,
) -> None:
    handle.write("# run.start\n")
    handle.write(f"# run.run_id: {run_id}\n")
    handle.write(f"# run.file_stem: {request.file_stem}\n")
    handle.write(f"# run.system_start_timestamp_utc: {_string_value(session_start_utc)}\n")
    handle.write(f"# run.frame_limit: {_string_value(request.frame_limit)}\n")
    handle.write(f"# run.duration_seconds: {_string_value(request.duration_seconds)}\n")
    handle.write(f"# run.target_frame_rate: {_string_value(request.target_frame_rate)}\n")
    handle.flush()


def append_recording_trace_image_row(
    writer: csv.writer,
    handle: TextIO,
    run_id: str,
    image_name: str,
    frame: CapturedFrame,
) -> None:
    writer.writerow(
        [
            run_id,
            image_name,
            frame.frame_id,
            frame.camera_timestamp,
            frame.timestamp_utc.isoformat(),
        ]
    )
    handle.flush()


def append_recording_trace_run_end(
    handle: TextIO,
    run_id: str,
    status: RecordingStatus,
    session_end_utc: str | None,
    end_state: str,
) -> None:
    handle.write("# run.end\n")
    handle.write(f"# run.run_id: {run_id}\n")
    handle.write(f"# run.system_end_timestamp_utc: {_string_value(session_end_utc)}\n")
    handle.write(f"# run.end_state: {end_state}\n")
    handle.write(f"# run.frames_written: {status.frames_written}\n")
    handle.write(f"# run.dropped_frames: {status.dropped_frames}\n")
    handle.write(f"# run.last_error: {_string_value(status.last_error)}\n")
    handle.flush()


def _iter_recording_trace_candidates(save_directory: Path):
    yield save_directory / f"{_RECORDING_TRACE_LOG_STEM}{_RECORDING_TRACE_LOG_SUFFIX}"
    for index in range(1, 1000):
        yield save_directory / f"{_RECORDING_TRACE_LOG_STEM}_{index:03d}{_RECORDING_TRACE_LOG_SUFFIX}"


def _read_recording_stable_context(path: Path) -> dict[str, str]:
    context: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("# context."):
            if context:
                break
            continue
        key, _, value = line[len("# context.") :].partition(":")
        context[key.strip()] = value.strip()
    return context


def _configuration_value(configuration: CameraConfiguration | None, field_name: str):
    if configuration is None:
        return None
    return getattr(configuration, field_name)


def _string_value(value) -> str:
    if value is None:
        return ""
    return str(value)


def _write_json_record(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")


__all__ = [
    "append_recording_trace_image_row",
    "append_recording_trace_run_end",
    "append_recording_trace_run_start",
    "build_recording_stable_context",
    "build_snapshot_trace_path",
    "open_recording_trace_log",
    "resolve_recording_trace_log_path",
    "write_snapshot_trace_sidecar",
]
