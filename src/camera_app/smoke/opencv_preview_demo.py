from __future__ import annotations

from pathlib import Path
from time import sleep

from camera_app.drivers.simulated_camera_driver import SimulatedCameraDriver
from camera_app.imaging.opencv_preview import OpenCvPreviewWindow
from camera_app.smoke.demo_result import DemoRunResult
from camera_app.services.preview_service import PreviewService


def run_opencv_preview_demo(
    sample_dir: Path | None = None,
    poll_interval_seconds: float = 0.03,
    frame_limit: int | None = None,
) -> DemoRunResult:
    sample_paths = []
    if sample_dir is not None:
        sample_paths = sorted(
            path for path in sample_dir.iterdir() if path.is_file() and path.suffix.lower() in {".pgm", ".ppm"}
        )

    driver = SimulatedCameraDriver(sample_image_paths=sample_paths)
    driver.initialize()

    preview_service = PreviewService(driver, poll_interval_seconds=poll_interval_seconds)
    preview_window = OpenCvPreviewWindow(preview_service)

    rendered_frames = 0
    preview_service.start()
    try:
        while frame_limit is None or rendered_frames < frame_limit:
            if preview_window.render_latest_frame(delay_ms=1):
                rendered_frames += 1
            sleep(poll_interval_seconds)
    finally:
        preview_window.close()
        preview_service.stop()
        driver.shutdown()

    return DemoRunResult(success=True, rendered_frames=rendered_frames)
