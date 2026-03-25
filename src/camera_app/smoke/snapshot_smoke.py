from __future__ import annotations

import argparse
from pathlib import Path

from camera_app.drivers.vimbax_camera_driver import VimbaXCameraDriver
from camera_app.logging.log_service import configure_logging
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.snapshot_request import SnapshotRequest
from camera_app.services.camera_service import CameraService
from camera_app.services.snapshot_service import SnapshotService


def run_snapshot_smoke(
    camera_id: str,
    save_directory: Path,
    file_stem: str,
    configuration: CameraConfiguration | None = None,
    file_extension: str = ".png",
    camera_service: CameraService | None = None,
    snapshot_service: SnapshotService | None = None,
) -> Path:
    owns_services = camera_service is None or snapshot_service is None
    driver = VimbaXCameraDriver() if owns_services else None
    camera_service = camera_service or CameraService(driver)
    snapshot_service = snapshot_service or SnapshotService(driver)

    try:
        camera_service.initialize(camera_id=camera_id)
        if configuration is not None:
            camera_service.apply_configuration(configuration)

        request = SnapshotRequest(
            save_directory=save_directory,
            file_stem=file_stem,
            file_extension=file_extension,
            camera_id=camera_id,
        )
        return snapshot_service.save_snapshot(request)
    finally:
        camera_service.shutdown()


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a minimal end-to-end snapshot smoke test.")
    parser.add_argument("--camera-id", default="cam2", help="Camera identifier to open. Default: cam2")
    parser.add_argument(
        "--save-directory",
        type=Path,
        required=True,
        help="Explicit target directory for the smoke-test snapshot.",
    )
    parser.add_argument("--file-stem", default="smoke_snapshot", help="Base filename without extension.")
    parser.add_argument("--file-extension", default=".png", help="Target file extension, for example .png or .raw.")
    parser.add_argument("--exposure-time-us", type=float, default=None, help="Optional exposure time to apply.")
    parser.add_argument("--gain", type=float, default=None, help="Optional gain to apply.")
    parser.add_argument("--pixel-format", default=None, help="Optional pixel format to apply, for example Mono8.")
    parser.add_argument(
        "--acquisition-frame-rate",
        type=float,
        default=None,
        help="Optional acquisition frame rate to apply.",
    )
    return parser


def main() -> int:
    configure_logging()
    parser = _build_argument_parser()
    args = parser.parse_args()

    configuration = CameraConfiguration(
        exposure_time_us=args.exposure_time_us,
        gain=args.gain,
        pixel_format=args.pixel_format,
        acquisition_frame_rate=args.acquisition_frame_rate,
    )
    if configuration == CameraConfiguration():
        configuration = None

    saved_path = run_snapshot_smoke(
        camera_id=args.camera_id,
        save_directory=args.save_directory,
        file_stem=args.file_stem,
        configuration=configuration,
        file_extension=args.file_extension,
    )
    print(saved_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
