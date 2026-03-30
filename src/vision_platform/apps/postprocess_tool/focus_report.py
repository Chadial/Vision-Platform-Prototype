from __future__ import annotations

import argparse
import struct
from dataclasses import dataclass
from pathlib import Path

from vision_platform.integrations.camera import SimulatedCameraDriver
from vision_platform.libraries.common_models import FocusRequest, RoiDefinition
from vision_platform.libraries.focus_core import evaluate_focus
from vision_platform.models import CapturedFrame
from vision_platform.services.recording_service.traceability import TraceArtifactRow, load_trace_logs_for_directory


@dataclass(slots=True)
class PostprocessFocusReportEntry:
    source_path: Path
    method: str
    score: float
    is_valid: bool
    roi_id: str | None
    frame_width: int
    frame_height: int
    pixel_format: str | None
    artifact_kind: str | None = None
    run_id: str | None = None
    frame_id: str | None = None
    camera_timestamp: str | None = None
    system_timestamp_utc: str | None = None
    analysis_roi_type: str | None = None
    analysis_roi_data: str | None = None
    focus_method: str | None = None
    focus_score_frame_interval: str | None = None
    focus_value_mean: str | None = None
    focus_value_stddev: str | None = None


@dataclass(slots=True)
class PostprocessFocusReportContext:
    record_kind: str | None = None
    camera_id: str | None = None
    pixel_format: str | None = None
    exposure_time_us: str | None = None
    gain: str | None = None
    roi_x: str | None = None
    roi_y: str | None = None
    roi_width: str | None = None
    roi_height: str | None = None


@dataclass(slots=True)
class PostprocessFocusReportSummary:
    total_entries: int
    valid_entries: int
    traceability_joined_entries: int
    best_source_path: Path | None = None
    best_score: float | None = None


@dataclass(slots=True)
class PostprocessFocusReport:
    sample_dir: Path
    entries: list[PostprocessFocusReportEntry]
    summary: PostprocessFocusReportSummary
    stable_context: PostprocessFocusReportContext | None = None


def run_focus_report(
    sample_dir: Path,
    method: str = "laplace",
    roi: RoiDefinition | None = None,
) -> list[PostprocessFocusReportEntry]:
    return run_focus_report_bundle(sample_dir, method=method, roi=roi).entries


def run_focus_report_bundle(
    sample_dir: Path,
    method: str = "laplace",
    roi: RoiDefinition | None = None,
) -> PostprocessFocusReport:
    sample_paths = _collect_sample_paths(sample_dir)
    traceability_data = load_trace_logs_for_directory(sample_dir)
    traceability_rows = traceability_data.rows_by_image_name
    entries: list[PostprocessFocusReportEntry] = []
    request = FocusRequest(method=method, roi=roi)
    for sample_path in sample_paths:
        frame = _load_focus_frame(sample_path)
        result = evaluate_focus(frame, request=request)
        artifact_row = traceability_rows.get(sample_path.name)
        entries.append(
            PostprocessFocusReportEntry(
                source_path=sample_path,
                method=result.method,
                score=result.score,
                is_valid=result.is_valid,
                roi_id=result.roi_id,
                frame_width=frame.width,
                frame_height=frame.height,
                pixel_format=frame.pixel_format,
                artifact_kind=artifact_row.artifact_kind if artifact_row is not None else None,
                run_id=artifact_row.run_id if artifact_row is not None else None,
                frame_id=artifact_row.frame_id if artifact_row is not None else None,
                camera_timestamp=artifact_row.camera_timestamp if artifact_row is not None else None,
                system_timestamp_utc=artifact_row.system_timestamp_utc if artifact_row is not None else None,
                analysis_roi_type=_metadata_value(artifact_row, "analysis_roi_type"),
                analysis_roi_data=_metadata_value(artifact_row, "analysis_roi_data"),
                focus_method=_metadata_value(artifact_row, "focus_method"),
                focus_score_frame_interval=_metadata_value(artifact_row, "focus_score_frame_interval"),
                focus_value_mean=_metadata_value(artifact_row, "focus_value_mean"),
                focus_value_stddev=_metadata_value(artifact_row, "focus_value_stddev"),
            )
        )
    return PostprocessFocusReport(
        sample_dir=sample_dir,
        entries=entries,
        summary=_build_report_summary(entries),
        stable_context=_build_report_context(traceability_data.stable_context),
    )


def format_focus_report(entries: list[PostprocessFocusReportEntry]) -> str:
    lines = [
        (
            f"{entry.source_path.name}: method={entry.method} "
            f"score={entry.score:.6f} valid={str(entry.is_valid).lower()} "
            f"size={entry.frame_width}x{entry.frame_height} pixel_format={entry.pixel_format or '-'}"
            f"{_format_optional_metadata(entry)}"
        )
        for entry in entries
    ]
    return "\n".join(lines)


def format_focus_report_bundle(report: PostprocessFocusReport) -> str:
    lines: list[str] = []
    lines.append(_format_report_summary(report.summary))
    context_line = _format_stable_context(report.stable_context)
    if context_line is not None:
        lines.append(context_line)
    entry_lines = format_focus_report(report.entries)
    if entry_lines:
        lines.append(entry_lines)
    return "\n".join(lines)


def _build_report_summary(entries: list[PostprocessFocusReportEntry]) -> PostprocessFocusReportSummary:
    best_entry = max(entries, key=lambda entry: entry.score, default=None)
    return PostprocessFocusReportSummary(
        total_entries=len(entries),
        valid_entries=sum(1 for entry in entries if entry.is_valid),
        traceability_joined_entries=sum(1 for entry in entries if entry.artifact_kind is not None),
        best_source_path=best_entry.source_path if best_entry is not None else None,
        best_score=best_entry.score if best_entry is not None else None,
    )


def _collect_sample_paths(sample_dir: Path) -> list[Path]:
    if not sample_dir.exists() or not sample_dir.is_dir():
        raise ValueError(f"Sample directory '{sample_dir}' does not exist or is not a directory.")

    sample_paths = sorted([*sample_dir.glob("*.pgm"), *sample_dir.glob("*.ppm"), *sample_dir.glob("*.bmp")])
    if not sample_paths:
        raise ValueError(f"Sample directory '{sample_dir}' does not contain any .pgm, .ppm, or .bmp files.")
    return sample_paths


def _load_focus_frame(sample_path: Path) -> CapturedFrame:
    suffix = sample_path.suffix.lower()
    if suffix in {".pgm", ".ppm"}:
        return _load_sample_frame(sample_path)
    if suffix == ".bmp":
        return _load_bmp_frame(sample_path)
    raise ValueError(f"Unsupported offline focus input '{sample_path.name}'.")


def _load_sample_frame(sample_path: Path) -> CapturedFrame:
    driver = SimulatedCameraDriver(sample_image_paths=[sample_path], loop_samples=False)
    driver.initialize(camera_id="postprocess-focus-report")
    try:
        return driver.capture_snapshot()
    finally:
        driver.shutdown()


def _load_bmp_frame(sample_path: Path) -> CapturedFrame:
    payload = sample_path.read_bytes()
    if len(payload) < 54 or payload[:2] != b"BM":
        raise RuntimeError(f"Unsupported BMP input '{sample_path.name}'.")

    pixel_offset = struct.unpack_from("<I", payload, 10)[0]
    dib_header_size = struct.unpack_from("<I", payload, 14)[0]
    if dib_header_size < 40 or len(payload) < 14 + dib_header_size:
        raise RuntimeError(f"Unsupported BMP DIB header in '{sample_path.name}'.")

    width, height = struct.unpack_from("<ii", payload, 18)
    planes, bits_per_pixel, compression = struct.unpack_from("<HHI", payload, 26)
    if planes != 1 or width <= 0 or height == 0:
        raise RuntimeError(f"Unsupported BMP geometry in '{sample_path.name}'.")
    if compression != 0 or bits_per_pixel not in {8, 24}:
        raise RuntimeError(f"Unsupported BMP encoding in '{sample_path.name}'.")

    top_down = height < 0
    frame_height = abs(height)
    bytes_per_pixel = 1 if bits_per_pixel == 8 else 3
    row_stride = width * bytes_per_pixel
    padded_row_stride = (row_stride + 3) & ~3
    expected_size = padded_row_stride * frame_height
    if pixel_offset + expected_size > len(payload):
        raise RuntimeError(f"BMP pixel data is truncated in '{sample_path.name}'.")

    rows: list[bytes] = []
    for row_index in range(frame_height):
        row_start = pixel_offset + (row_index * padded_row_stride)
        rows.append(payload[row_start : row_start + row_stride])
    if not top_down:
        rows.reverse()

    pixel_bytes = b"".join(rows)
    pixel_format = "Mono8" if bits_per_pixel == 8 else "Bgr8"
    return CapturedFrame(
        raw_frame=pixel_bytes,
        width=width,
        height=frame_height,
        pixel_format=pixel_format,
    )


def _metadata_value(artifact_row: TraceArtifactRow | None, field_name: str) -> str | None:
    if artifact_row is None:
        return None
    return getattr(artifact_row.metadata, field_name)


def _build_report_context(stable_context: dict[str, str]) -> PostprocessFocusReportContext | None:
    if not stable_context:
        return None
    context = PostprocessFocusReportContext(
        record_kind=_context_value(stable_context, "record_kind"),
        camera_id=_context_value(stable_context, "camera_id"),
        pixel_format=_context_value(stable_context, "pixel_format"),
        exposure_time_us=_context_value(stable_context, "exposure_time_us"),
        gain=_context_value(stable_context, "gain"),
        roi_x=_context_value(stable_context, "roi_x"),
        roi_y=_context_value(stable_context, "roi_y"),
        roi_width=_context_value(stable_context, "roi_width"),
        roi_height=_context_value(stable_context, "roi_height"),
    )
    if not any(
        (
            context.record_kind,
            context.camera_id,
            context.pixel_format,
            context.exposure_time_us,
            context.gain,
            context.roi_x,
            context.roi_y,
            context.roi_width,
            context.roi_height,
        )
    ):
        return None
    return context


def _context_value(stable_context: dict[str, str], field_name: str) -> str | None:
    value = stable_context.get(field_name)
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _format_optional_metadata(entry: PostprocessFocusReportEntry) -> str:
    metadata_parts: list[str] = []
    if entry.artifact_kind:
        metadata_parts.append(f" artifact_kind={entry.artifact_kind}")
    if entry.run_id:
        metadata_parts.append(f" run_id={entry.run_id}")
    if entry.frame_id:
        metadata_parts.append(f" frame_id={entry.frame_id}")
    if entry.camera_timestamp:
        metadata_parts.append(f" camera_timestamp={entry.camera_timestamp}")
    if entry.system_timestamp_utc:
        metadata_parts.append(f" system_timestamp_utc={entry.system_timestamp_utc}")
    if entry.analysis_roi_type:
        metadata_parts.append(f" analysis_roi_type={entry.analysis_roi_type}")
    if entry.analysis_roi_data:
        metadata_parts.append(f" analysis_roi_data={entry.analysis_roi_data}")
    if entry.focus_method:
        metadata_parts.append(f" focus_method={entry.focus_method}")
    if entry.focus_score_frame_interval:
        metadata_parts.append(f" focus_score_frame_interval={entry.focus_score_frame_interval}")
    if entry.focus_value_mean:
        metadata_parts.append(f" focus_value_mean={entry.focus_value_mean}")
    if entry.focus_value_stddev:
        metadata_parts.append(f" focus_value_stddev={entry.focus_value_stddev}")
    return "".join(metadata_parts)


def _format_stable_context(context: PostprocessFocusReportContext | None) -> str | None:
    if context is None:
        return None
    parts: list[str] = []
    if context.record_kind:
        parts.append(f"record_kind={context.record_kind}")
    if context.camera_id:
        parts.append(f"camera_id={context.camera_id}")
    if context.pixel_format:
        parts.append(f"pixel_format={context.pixel_format}")
    if context.exposure_time_us:
        parts.append(f"exposure_time_us={context.exposure_time_us}")
    if context.gain:
        parts.append(f"gain={context.gain}")
    if any((context.roi_x, context.roi_y, context.roi_width, context.roi_height)):
        parts.append(
            "roi="
            f"({context.roi_x or '-'},"
            f"{context.roi_y or '-'},"
            f"{context.roi_width or '-'},"
            f"{context.roi_height or '-'})"
        )
    if not parts:
        return None
    return "context: " + " ".join(parts)


def _format_report_summary(summary: PostprocessFocusReportSummary) -> str:
    parts = [
        f"entries={summary.total_entries}",
        f"valid={summary.valid_entries}",
        f"traceability_joined={summary.traceability_joined_entries}",
    ]
    if summary.best_source_path is not None:
        parts.append(f"best={summary.best_source_path.name}")
    if summary.best_score is not None:
        parts.append(f"best_score={summary.best_score:.6f}")
    return "summary: " + " ".join(parts)


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a thin offline focus report over stored sample or BMP images.")
    parser.add_argument("sample_dir", type=Path, help="Directory containing .pgm, .ppm, or .bmp images.")
    parser.add_argument(
        "--method",
        default="laplace",
        help="Focus method to evaluate (`laplace` or `tenengrad`).",
    )
    return parser


def main() -> int:
    parser = _build_argument_parser()
    args = parser.parse_args()
    report = run_focus_report_bundle(sample_dir=args.sample_dir, method=args.method)
    print(format_focus_report_bundle(report))
    return 0


__all__ = [
    "PostprocessFocusReport",
    "PostprocessFocusReportContext",
    "PostprocessFocusReportEntry",
    "PostprocessFocusReportSummary",
    "format_focus_report",
    "format_focus_report_bundle",
    "main",
    "run_focus_report",
    "run_focus_report_bundle",
]
