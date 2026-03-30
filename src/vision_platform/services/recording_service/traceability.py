from __future__ import annotations

import csv
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import TextIO

from vision_platform.libraries.common_models import RoiDefinition
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
    "analysis_roi_id",
    "analysis_roi_type",
    "analysis_roi_data",
    "focus_method",
    "focus_score_frame_interval",
    "focus_value_mean",
    "focus_value_stddev",
    "focus_roi_type",
    "focus_roi_data",
]


@dataclass(slots=True)
class TraceArtifactMetadata:
    analysis_roi_id: str | None = None
    analysis_roi_type: str | None = None
    analysis_roi_data: str | None = None
    focus_method: str | None = None
    focus_score_frame_interval: str | None = None
    focus_value_mean: str | None = None
    focus_value_stddev: str | None = None
    focus_roi_type: str | None = None
    focus_roi_data: str | None = None


@dataclass(slots=True)
class TraceArtifactRow:
    artifact_kind: str
    run_id: str
    image_name: str
    frame_id: str | None
    camera_timestamp: str | None
    system_timestamp_utc: str | None
    metadata: TraceArtifactMetadata


@dataclass(slots=True)
class TraceLogData:
    stable_context: dict[str, str]
    rows_by_image_name: dict[str, TraceArtifactRow]


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
    artifact_metadata: TraceArtifactMetadata | None = None,
) -> None:
    metadata = artifact_metadata or TraceArtifactMetadata()
    _validate_focus_metadata(metadata)
    writer.writerow(
        [
            artifact_kind,
            run_id,
            image_name,
            frame.frame_id,
            frame.camera_timestamp,
            frame.timestamp_utc.isoformat(),
            _string_value(metadata.analysis_roi_id),
            _string_value(metadata.analysis_roi_type),
            _string_value(metadata.analysis_roi_data),
            _string_value(metadata.focus_method),
            _string_value(metadata.focus_score_frame_interval),
            _string_value(metadata.focus_value_mean),
            _string_value(metadata.focus_value_stddev),
            _string_value(metadata.focus_roi_type),
            _string_value(metadata.focus_roi_data),
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
    artifact_metadata: TraceArtifactMetadata | None = None,
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
            artifact_metadata=artifact_metadata,
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


def iter_trace_log_paths(save_directory: Path) -> list[Path]:
    return sorted(path for path in save_directory.glob(f"{_TRACE_LOG_STEM}*{_TRACE_LOG_SUFFIX}") if path.is_file())


def load_trace_log(path: Path) -> TraceLogData:
    stable_context = _read_stable_context(path)
    row_lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line and not line.startswith("#")]
    if not row_lines:
        return TraceLogData(stable_context=stable_context, rows_by_image_name={})

    reader = csv.DictReader(row_lines)
    rows_by_image_name: dict[str, TraceArtifactRow] = {}
    for row in reader:
        image_name = (row.get("image_name") or "").strip()
        if not image_name:
            continue
        rows_by_image_name[image_name] = TraceArtifactRow(
            artifact_kind=(row.get("artifact_kind") or "").strip(),
            run_id=(row.get("run_id") or "").strip(),
            image_name=image_name,
            frame_id=_optional_string(row.get("frame_id")),
            camera_timestamp=_optional_string(row.get("camera_timestamp")),
            system_timestamp_utc=_optional_string(row.get("system_timestamp_utc")),
            metadata=TraceArtifactMetadata(
                analysis_roi_id=_optional_string(row.get("analysis_roi_id")),
                analysis_roi_type=_optional_string(row.get("analysis_roi_type")),
                analysis_roi_data=_optional_string(row.get("analysis_roi_data")),
                focus_method=_optional_string(row.get("focus_method")),
                focus_score_frame_interval=_optional_string(row.get("focus_score_frame_interval")),
                focus_value_mean=_optional_string(row.get("focus_value_mean")),
                focus_value_stddev=_optional_string(row.get("focus_value_stddev")),
                focus_roi_type=_optional_string(row.get("focus_roi_type")),
                focus_roi_data=_optional_string(row.get("focus_roi_data")),
            ),
        )
    return TraceLogData(stable_context=stable_context, rows_by_image_name=rows_by_image_name)


def load_trace_logs_for_directory(save_directory: Path) -> TraceLogData:
    merged_context: dict[str, str] = {}
    rows_by_image_name: dict[str, TraceArtifactRow] = {}
    for path in iter_trace_log_paths(save_directory):
        log_data = load_trace_log(path)
        if not merged_context and log_data.stable_context:
            merged_context = dict(log_data.stable_context)
        rows_by_image_name.update(log_data.rows_by_image_name)
    return TraceLogData(stable_context=merged_context, rows_by_image_name=rows_by_image_name)


def build_trace_artifact_metadata(
    *,
    analysis_roi: RoiDefinition | None = None,
    focus_method: str | None = None,
    focus_score_frame_interval: int | str | None = None,
    focus_value_mean: float | str | None = None,
    focus_value_stddev: float | str | None = None,
    focus_roi: RoiDefinition | None = None,
) -> TraceArtifactMetadata:
    analysis_roi_type, analysis_roi_data = _serialize_roi(analysis_roi)
    focus_roi_type, focus_roi_data = _serialize_roi(focus_roi, default_type="global" if focus_method else None)
    metadata = TraceArtifactMetadata(
        analysis_roi_id=analysis_roi.roi_id if analysis_roi is not None else None,
        analysis_roi_type=analysis_roi_type,
        analysis_roi_data=analysis_roi_data,
        focus_method=focus_method,
        focus_score_frame_interval=_string_value(focus_score_frame_interval) if focus_score_frame_interval is not None else None,
        focus_value_mean=_string_value(focus_value_mean) if focus_value_mean is not None else None,
        focus_value_stddev=_string_value(focus_value_stddev) if focus_value_stddev is not None else None,
        focus_roi_type=focus_roi_type,
        focus_roi_data=focus_roi_data,
    )
    _validate_focus_metadata(metadata)
    return metadata


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


def _optional_string(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _serialize_roi(
    roi: RoiDefinition | None,
    default_type: str | None = None,
) -> tuple[str | None, str | None]:
    if roi is None:
        return default_type, None

    points = tuple(roi.points)
    if roi.shape in {"rectangle", "ellipse"} and len(points) >= 2:
        first, second = points[0], points[1]
        return roi.shape, (
            f"{roi.shape}("
            f"{_format_coordinate(first[0])},{_format_coordinate(first[1])},"
            f"{_format_coordinate(second[0])},{_format_coordinate(second[1])})"
        )

    if points:
        serialized_points = ",".join(
            f"{_format_coordinate(x)},{_format_coordinate(y)}" for x, y in points
        )
        return roi.shape, f"{roi.shape}({serialized_points})"

    return roi.shape, roi.shape


def _validate_focus_metadata(metadata: TraceArtifactMetadata) -> None:
    has_summary_values = metadata.focus_value_mean is not None or metadata.focus_value_stddev is not None
    if has_summary_values:
        if metadata.focus_score_frame_interval is None:
            raise ValueError(
                "focus_value_mean and focus_value_stddev require an explicit aggregation basis such as focus_score_frame_interval."
            )
        if not _has_text(metadata.focus_method):
            raise ValueError("focus summary metadata requires focus_method when summary values are stored.")

    if metadata.focus_score_frame_interval is not None:
        _parse_positive_int(
            metadata.focus_score_frame_interval,
            field_name="focus_score_frame_interval",
        )

    if metadata.focus_value_stddev is not None:
        stddev = _parse_float(metadata.focus_value_stddev, field_name="focus_value_stddev")
        if stddev < 0:
            raise ValueError("focus_value_stddev must be non-negative when provided.")


def _format_coordinate(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return format(value, "g")


def _has_text(value: str | None) -> bool:
    return value is not None and bool(value.strip())


def _parse_positive_int(value: str, *, field_name: str) -> int:
    stripped = value.strip()
    try:
        parsed = int(stripped)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a positive integer when provided.") from exc
    if str(parsed) != stripped or parsed <= 0:
        raise ValueError(f"{field_name} must be a positive integer when provided.")
    return parsed


def _parse_float(value: str, *, field_name: str) -> float:
    stripped = value.strip()
    try:
        parsed = float(stripped)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be numeric when provided.") from exc
    if not isfinite(parsed):
        raise ValueError(f"{field_name} must be numeric when provided.")
    return parsed


__all__ = [
    "TraceArtifactMetadata",
    "TraceArtifactRow",
    "TraceLogData",
    "append_trace_image_row",
    "append_trace_run_end",
    "append_trace_run_start",
    "build_trace_artifact_metadata",
    "build_recording_stable_context",
    "build_snapshot_stable_context",
    "iter_trace_log_paths",
    "load_trace_log",
    "load_trace_logs_for_directory",
    "open_trace_log",
    "record_snapshot_trace",
    "resolve_trace_log_path",
]
