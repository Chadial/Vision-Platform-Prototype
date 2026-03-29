from __future__ import annotations

import argparse
from pathlib import Path
from time import sleep

from camera_app.logging.log_service import configure_logging
from camera_app.smoke.demo_result import DemoRunResult
from vision_platform.apps.opencv_prototype.preview_snapshot import PreviewSnapshotSaver
from vision_platform.imaging.opencv_preview import OpenCvPreviewWindow
from vision_platform.integrations.camera import SimulatedCameraDriver
from vision_platform.libraries.common_models import RoiDefinition
from vision_platform.services.stream_service import CameraStreamService


def _format_operator_error(exc: Exception) -> str:
    message = str(exc).strip()
    if message:
        return message
    return exc.__class__.__name__


def run_opencv_preview_demo(
    sample_dir: Path | None = None,
    poll_interval_seconds: float = 0.03,
    frame_limit: int | None = None,
    include_focus_state: bool = False,
    roi: RoiDefinition | None = None,
    snapshot_save_directory: Path | None = None,
    snapshot_file_stem: str = "preview_snapshot",
    snapshot_file_extension: str = ".png",
) -> DemoRunResult:
    sample_paths = []
    if sample_dir is not None:
        sample_paths = sorted(
            path for path in sample_dir.iterdir() if path.is_file() and path.suffix.lower() in {".pgm", ".ppm"}
        )

    driver = SimulatedCameraDriver(sample_image_paths=sample_paths)
    driver.initialize()
    stream_service = CameraStreamService(
        driver,
        preview_poll_interval_seconds=poll_interval_seconds,
        shared_poll_interval_seconds=poll_interval_seconds,
    )
    snapshot_saver = None
    if snapshot_save_directory is not None:
        snapshot_saver = PreviewSnapshotSaver(
            stream_service._preview_service,
            save_directory=snapshot_save_directory,
            file_stem=snapshot_file_stem,
            file_extension=snapshot_file_extension,
        )
    preview_window = OpenCvPreviewWindow(
        stream_service._preview_service,
        roi_state_service=stream_service.get_roi_state_service(),
        snapshot_callback=snapshot_saver.save_latest_frame if snapshot_saver is not None else None,
    )
    focus_preview_service = stream_service.create_focus_preview_service() if include_focus_state else None
    if focus_preview_service is not None:
        preview_window = OpenCvPreviewWindow(
            stream_service._preview_service,
            focus_state_provider=focus_preview_service.get_latest_focus_state,
            roi_state_service=stream_service.get_roi_state_service(),
            snapshot_callback=snapshot_saver.save_latest_frame if snapshot_saver is not None else None,
        )

    rendered_frames = 0
    latest_focus_state = None
    preview_started = False
    try:
        stream_service.start_preview()
        preview_started = True
        while frame_limit is None or rendered_frames < frame_limit:
            if focus_preview_service is not None:
                latest_focus_state = focus_preview_service.refresh_once(roi=roi)
            if preview_window.render_latest_frame(delay_ms=1):
                rendered_frames += 1
            sleep(poll_interval_seconds)
    finally:
        preview_window.close()
        if preview_started:
            stream_service.stop_preview()
        driver.shutdown()

    return DemoRunResult(
        success=True,
        rendered_frames=rendered_frames,
        preview_frame_info=stream_service.get_latest_frame_info(),
        focus_preview_state=latest_focus_state,
    )


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the optional OpenCV preview demo with the simulated driver.")
    parser.add_argument(
        "--sample-dir",
        type=Path,
        default=None,
        help="Optional directory containing .pgm or .ppm sample images.",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        type=float,
        default=0.03,
        help="Preview polling interval in seconds.",
    )
    parser.add_argument(
        "--frame-limit",
        type=int,
        default=None,
        help="Optional number of rendered frames before the demo exits.",
    )
    parser.add_argument(
        "--with-focus",
        action="store_true",
        help="Also compute focus state during preview rendering.",
    )
    parser.add_argument(
        "--snapshot-save-directory",
        type=Path,
        default=None,
        help="Optional directory that enables the '+' snapshot shortcut for saving the latest preview frame.",
    )
    parser.add_argument(
        "--snapshot-file-stem",
        default="preview_snapshot",
        help="Base file stem used by the '+' snapshot shortcut when a snapshot save directory is configured.",
    )
    parser.add_argument(
        "--snapshot-file-extension",
        default=".png",
        help="File extension used by the '+' snapshot shortcut when a snapshot save directory is configured.",
    )
    return parser


def main() -> int:
    configure_logging()
    parser = _build_argument_parser()
    args = parser.parse_args()
    shortcut_hint = OpenCvPreviewWindow.build_shortcut_hint(
        has_snapshot_shortcut=args.snapshot_save_directory is not None,
        has_focus_toggle=args.with_focus,
    )
    print(
        "Preview controls: left click=select point, "
        f"{shortcut_hint}, q/Esc or window close=quit"
    )

    try:
        result = run_opencv_preview_demo(
            sample_dir=args.sample_dir,
            poll_interval_seconds=args.poll_interval_seconds,
            frame_limit=args.frame_limit,
            include_focus_state=args.with_focus,
            snapshot_save_directory=args.snapshot_save_directory,
            snapshot_file_stem=args.snapshot_file_stem,
            snapshot_file_extension=args.snapshot_file_extension,
        )
    except Exception as exc:
        print(f"ERROR: Preview demo failed: {_format_operator_error(exc)}")
        return 1
    print(f"Rendered {result.rendered_frames} frames.")
    if result.focus_preview_state is not None:
        print(result.focus_preview_state.result.score)
    return 0


__all__ = ["main", "run_opencv_preview_demo"]


if __name__ == "__main__":
    raise SystemExit(main())
