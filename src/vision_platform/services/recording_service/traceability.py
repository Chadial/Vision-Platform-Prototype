from __future__ import annotations

import csv
from pathlib import Path
from typing import TextIO

from vision_platform.models import CameraConfiguration, CapturedFrame, RecordingRequest, SnapshotRequest

_TRACE_LOG_STEM = "saved_artifact_traceability"
_TRACE_LOG_SUFFIX = ".csv"
_TRACE_ROW_HEADER = [
    "artifact_kind",
    "run_id",
    "image_name",
    "frame_id",
    "camera_timestamp",
    "system_timestamp_utc",
]


def resolve_trace_log_path(
    save_directory: Path | None,
    stable_context: dict[str, str],
) -> tuple[Path, bool]:
    if save_directory is None:
        raise ValueError("save_directory must be set before resolving a traceability log.")

    candidate_paths = list(_iter_trace_candidates(save_directory))
    for candidate in candidate_paths:
        if candidate.exists() and _read_stable_context(candidate) == stable_context:
            return candidate, True

    for candidate in candidate_paths:
        if not candidate.exists():
            return candidate, False

    raise RuntimeError("Unable to resolve a saved artifact traceability log path.")


def build_snapshot_stable_context(
    request: SnapshotRequest,
    configuration: CameraConfiguration | None,
) -> dict[str, str]:
    return {
        "record_kind": "saved_artifact_folder_log",
        "save_directory": str(request.save_directory),
        "camera_id": _string_value(request.camera_id),
        "pixel_format": _string_value(_configuration_value(configuration, "pixel_format")),
        "exposure_time_us": _string_value(_configuration_value(configuration, "exposure_time_us")),
        "gain": _string_value(_configuration_value(configuration, "gain")),
        "roi_x": _string_value(_configuration_value(configuration, "roi_offset_x")),
        "roi_y": _string_value(_configuration_value(configuration, "roi_offset_y")),
        "roi_width": _string_value(_configuration_value(configuration, "roi_width")),
        "roi_height": _string_value(_configuration_value(configuration, "roi_height")),
    }


def build_recording_stable_context(
    request: RecordingRequest,
    configuration: CameraConfiguration | None,
) -> dict[str, str]:
    return {
        "record_kind": "saved_artifact_folder_log",
        "save_directory": str(request.save_directory),
        "camera_id": _string_value(request.camera_id),
        "pixel_format": _string_value(_configuration_value(configuration, "pixel_format")),
        "exposure_time_us": _string_value(_configuration_value(configuration, "exposure_time_us")),
        "gain": _string_value(_configuration_value(configuration, "gain")),
        "roi_x": _string_value(_configuration_value(configuration, "roi_offset_x")),
        "roi_y": _string_value(_configuration_value(configuration, "roi_offset_y")),
        "roi_width": _string_value(_configuration_value(configuration, "roi_width")),
        "roi_height": _string_value(_configuration_value(configuration, "roi_height")),
    }


def open_trace_log(
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
        writer.writerow(_TRACE_ROW_HEADER)
        handle.flush()
    return handle, writer


def append_trace_run_start(
    handle: TextIO,
    artifact_kind: str,
    run_id: str,
    file_stem: str,
    session_start_utc: str | None,
    frame_limit: int | None,
    duration_seconds: float | None,
    target_frame_rate: float | None,
) -> None:
    handle.write("# run.start\n")
    handle.write(f"# run.artifact_kind: {artifact_kind}\n")
    handle.write(f"# run.run_id: {run_id}\n")
    handle.write(f"# run.file_stem: {file_stem}\n")
    handle.write(f"# run.system_start_timestamp_utc: {_string_value(session_start_utc)}\n")
    handle.write(f"# run.frame_limit: {_string_value(frame_limit)}\n")
    handle.write(f"# run.duration_seconds: {_string_value(duration_seconds)}\n")
    handle.write(f"# run.target_frame_rate: {_string_value(target_frame_rate)}\n")
    handle.flush()


def append_trace_image_row(
    writer: csv.writer,
    handle: TextIO,
    artifact_kind: str,
    run_id: str,
    image_name: str,
    frame: CapturedFrame,
) -> None:
    writer.writerow(
        [
            artifact_kind,
            run_id,
            image_name,
            frame.frame_id,
            frame.camera_timestamp,
            frame.timestamp_utc.isoformat(),
        ]
    )
    handle.flush()


def append_trace_run_end(
    handle: TextIO,
    artifact_kind: str,
    run_id: str,
    frames_written: int,
    dropped_frames: int,
    last_error: str | None,
    session_end_utc: str | None,
    end_state: str,
) -> None:
    handle.write("# run.end\n")
    handle.write(f"# run.artifact_kind: {artifact_kind}\n")
    handle.write(f"# run.run_id: {run_id}\n")
    handle.write(f"# run.system_end_timestamp_utc: {_string_value(session_end_utc)}\n")
    handle.write(f"# run.end_state: {end_state}\n")
    handle.write(f"# run.frames_written: {frames_written}\n")
    handle.write(f"# run.dropped_frames: {dropped_frames}\n")
    handle.write(f"# run.last_error: {_string_value(last_error)}\n")
    handle.flush()


def record_snapshot_trace(
    saved_path: Path,
    request: SnapshotRequest,
    frame: CapturedFrame,
    configuration: CameraConfiguration | None,
) -> Path:
    stable_context = build_snapshot_stable_context(request, configuration)
    log_path, reused_existing_log = resolve_trace_log_path(request.save_directory, stable_context)
    handle, writer = open_trace_log(log_path, stable_context, reused_existing_log=reused_existing_log)
    run_id = saved_path.stem
    try:
        append_trace_run_start(
            handle,
            artifact_kind="snapshot",
            run_id=run_id,
            file_stem=saved_path.stem,
            session_start_utc=frame.timestamp_utc.isoformat(),
            frame_limit=1,
            duration_seconds=None,
            target_frame_rate=None,
        )
        append_trace_image_row(
            writer,
            handle,
            artifact_kind="snapshot",
            run_id=run_id,
            image_name=saved_path.name,
            frame=frame,
        )
        append_trace_run_end(
            handle,
            artifact_kind="snapshot",
            run_id=run_id,
            frames_written=1,
            dropped_frames=0,
            last_error=None,
            session_end_utc=frame.timestamp_utc.isoformat(),
            end_state="completed",
        )
        return log_path
    finally:
        handle.close()


def _iter_trace_candidates(save_directory: Path):
    yield save_directory / f"{_TRACE_LOG_STEM}{_TRACE_LOG_SUFFIX}"
    for index in range(1, 1000):
        yield save_directory / f"{_TRACE_LOG_STEM}_{index:03d}{_TRACE_LOG_SUFFIX}"


def _read_stable_context(path: Path) -> dict[str, str]:
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


__all__ = [
    "append_trace_image_row",
    "append_trace_run_end",
    "append_trace_run_start",
    "build_recording_stable_context",
    "build_snapshot_stable_context",
    "open_trace_log",
    "record_snapshot_trace",
    "resolve_trace_log_path",
]
