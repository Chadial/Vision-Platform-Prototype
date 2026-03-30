from __future__ import annotations

import argparse
from pathlib import Path
from time import sleep

from camera_app.logging.log_service import configure_logging
from vision_platform.apps.opencv_prototype.demo_result import DemoRunResult
from vision_platform.integrations.camera import SimulatedCameraDriver
from vision_platform.libraries.common_models import DisplayOverlayPayload, RoiDefinition
from vision_platform.services.display_service import OverlayCompositionService
from vision_platform.services.recording_service import SnapshotFocusService
from vision_platform.services.stream_service import CameraStreamService


def run_overlay_payload_demo(
    sample_dir: Path | None = None,
    poll_interval_seconds: float = 0.01,
    roi: RoiDefinition | None = None,
) -> DemoRunResult:
    sample_paths = []
    if sample_dir is not None:
        sample_paths = sorted(
            path for path in sample_dir.iterdir() if path.is_file() and path.suffix.lower() in {".pgm", ".ppm"}
        )

    driver = SimulatedCameraDriver(sample_image_paths=sample_paths)
    driver.initialize(camera_id="sim-overlay-payload")
    stream_service = CameraStreamService(
        driver,
        preview_poll_interval_seconds=poll_interval_seconds,
        shared_poll_interval_seconds=poll_interval_seconds,
    )
    roi_state_service = stream_service.get_roi_state_service()
    if roi is not None:
        roi_state_service.set_active_roi(roi)
    focus_preview_service = stream_service.create_focus_preview_service()
    snapshot_focus_service = SnapshotFocusService(driver, roi_state_service=roi_state_service)
    overlay_composition_service = OverlayCompositionService(roi_state_service=roi_state_service)

    stream_service.start_preview()
    try:
        preview_focus_state = None
        preview_frame_info = None
        for _ in range(100):
            stream_service.refresh_preview_once()
            preview_frame_info = stream_service.get_latest_frame_info()
            preview_focus_state = focus_preview_service.refresh_once()
            if preview_focus_state is not None and preview_focus_state.result.is_valid:
                if preview_frame_info is None:
                    preview_frame_info = stream_service.get_latest_frame_info()
                break
            sleep(poll_interval_seconds)

        snapshot_focus_capture = snapshot_focus_service.capture_focus_state()
        display_overlay_payload = overlay_composition_service.compose(
            preview_focus_state=preview_focus_state,
            snapshot_focus_capture=snapshot_focus_capture,
        )

        return DemoRunResult(
            success=_overlay_payload_ready(display_overlay_payload),
            preview_frame_info=preview_frame_info,
            focus_preview_state=preview_focus_state,
            snapshot_focus_capture=snapshot_focus_capture,
            display_overlay_payload=display_overlay_payload,
        )
    finally:
        stream_service.stop_preview()
        driver.shutdown()


def summarize_overlay_payload(payload: DisplayOverlayPayload) -> str:
    """Build a compact console summary without committing to a UI toolkit."""

    active_roi_id = payload.active_roi.roi_id if payload.active_roi is not None else "-"
    preview_score = payload.preview_focus.score if payload.preview_focus is not None else None
    snapshot_score = payload.snapshot_focus.score if payload.snapshot_focus is not None else None
    return (
        f"active_roi={active_roi_id} "
        f"preview_focus={_format_optional_score(preview_score)} "
        f"snapshot_focus={_format_optional_score(snapshot_score)}"
    )


def _overlay_payload_ready(payload: DisplayOverlayPayload) -> bool:
    return payload.preview_focus is not None or payload.snapshot_focus is not None or payload.active_roi is not None


def _format_optional_score(score: float | None) -> str:
    if score is None:
        return "-"
    return f"{score:.6f}"


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a simulated display-overlay payload demo.")
    parser.add_argument(
        "--sample-dir",
        type=Path,
        default=None,
        help="Optional directory containing .pgm or .ppm sample images.",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        type=float,
        default=0.01,
        help="Preview and shared-stream polling interval in seconds.",
    )
    return parser


def main() -> int:
    configure_logging()
    parser = _build_argument_parser()
    args = parser.parse_args()
    result = run_overlay_payload_demo(
        sample_dir=args.sample_dir,
        poll_interval_seconds=args.poll_interval_seconds,
        roi=RoiDefinition(
            roi_id="demo-roi",
            shape="rectangle",
            points=((1.0, 1.0), (5.0, 1.0), (5.0, 5.0), (1.0, 5.0)),
        ),
    )
    if result.display_overlay_payload is not None:
        print(summarize_overlay_payload(result.display_overlay_payload))
    return 0 if result.success else 1


__all__ = ["main", "run_overlay_payload_demo", "summarize_overlay_payload"]
