from __future__ import annotations

import argparse
from pathlib import Path

from camera_app.drivers.simulated_camera_driver import SimulatedCameraDriver
from camera_app.imaging.opencv_adapter import OpenCvFrameAdapter
from camera_app.logging.log_service import configure_logging
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.snapshot_request import SnapshotRequest
from camera_app.smoke.demo_result import DemoRunResult
from camera_app.services.camera_service import CameraService
from camera_app.services.snapshot_service import SnapshotService
from camera_app.storage.frame_writer import FrameWriter


def run_opencv_save_demo(
    save_directory: Path,
    file_stem: str,
    pixel_format: str = "Mono16",
    file_extension: str = ".tiff",
) -> DemoRunResult:
    driver = SimulatedCameraDriver(pixel_format=pixel_format)
    camera_service = CameraService(driver)
    frame_writer = FrameWriter(opencv_adapter=OpenCvFrameAdapter())
    snapshot_service = SnapshotService(driver, frame_writer=frame_writer)

    try:
        camera_service.initialize(camera_id="sim-save-demo")
        camera_service.apply_configuration(CameraConfiguration(pixel_format=pixel_format))
        saved_path = snapshot_service.save_snapshot(
            SnapshotRequest(
                save_directory=save_directory,
                file_stem=file_stem,
                file_extension=file_extension,
            )
        )
        return DemoRunResult(success=True, saved_path=saved_path)
    finally:
        camera_service.shutdown()


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Save one simulated frame through the optional OpenCV-backed grayscale path."
    )
    parser.add_argument("--save-directory", type=Path, required=True, help="Output directory for the saved image.")
    parser.add_argument("--file-stem", default="opencv_save_demo", help="Base file name without extension.")
    parser.add_argument(
        "--pixel-format",
        default="Mono16",
        choices=["Mono8", "Mono16"],
        help="Simulated grayscale pixel format to save.",
    )
    parser.add_argument(
        "--file-extension",
        default=".tiff",
        choices=[".png", ".tif", ".tiff"],
        help="Lossless output format.",
    )
    return parser


def main() -> int:
    configure_logging()
    parser = _build_argument_parser()
    args = parser.parse_args()

    saved_path = run_opencv_save_demo(
        save_directory=args.save_directory,
        file_stem=args.file_stem,
        pixel_format=args.pixel_format,
        file_extension=args.file_extension,
    )
    print(saved_path.saved_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
