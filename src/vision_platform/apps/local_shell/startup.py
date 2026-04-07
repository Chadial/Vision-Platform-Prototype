from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from vision_platform.bootstrap import CameraSubsystem, build_camera_subsystem, build_simulated_camera_subsystem
from vision_platform.apps.camera_cli.camera_aliases import CameraAliasResolutionError, resolve_camera_id
from vision_platform.apps.camera_cli.camera_configuration_profiles import (
    CameraConfigurationProfileResolutionError,
    has_configuration_values,
    merge_configuration_requests,
    normalize_camera_class_name,
    resolve_camera_configuration_profile,
)
from vision_platform.models import ApplyConfigurationRequest, CameraStatus, SetSaveDirectoryRequest


@dataclass(slots=True)
class LocalShellLaunchOptions:
    source: str = "simulated"
    camera_id: str | None = None
    camera_alias: str | None = None
    sample_dir: Path | None = None
    configuration_profile: str | None = None
    profile_camera_class: str | None = None
    exposure_time_us: float | None = None
    gain: float | None = None
    pixel_format: str | None = None
    acquisition_frame_rate: float | None = None
    roi_offset_x: int | None = None
    roi_offset_y: int | None = None
    roi_width: int | None = None
    roi_height: int | None = None
    snapshot_directory: Path = Path("captures/wx_shell_snapshot")
    poll_interval_seconds: float = 0.03


@dataclass(slots=True)
class LocalShellSession:
    subsystem: CameraSubsystem
    source: str
    selected_save_directory: Path
    resolved_camera_id: str | None
    configuration_profile_id: str | None = None
    configuration_profile_camera_class: str | None = None


@dataclass(slots=True)
class LocalShellStartupError(Exception):
    message: str

    def __str__(self) -> str:
        return self.message


def build_local_shell_session(
    options: LocalShellLaunchOptions,
) -> LocalShellSession:
    _validate_launch_options(options)
    subsystem = _build_subsystem(options)
    try:
        resolved_camera_id = _resolve_camera_id(options)
        initialized_status = subsystem.camera_service.initialize(camera_id=resolved_camera_id)
        profile_identity = _apply_configuration_if_requested(
            subsystem.command_controller,
            options,
            initialized_status,
        )
        selected_save_directory = subsystem.command_controller.set_save_directory(
            SetSaveDirectoryRequest(
                base_directory=options.snapshot_directory,
                mode="append",
            )
        ).selected_directory
        return LocalShellSession(
            subsystem=subsystem,
            source=options.source,
            selected_save_directory=selected_save_directory,
            resolved_camera_id=resolved_camera_id,
            configuration_profile_id=profile_identity[0] if profile_identity is not None else None,
            configuration_profile_camera_class=profile_identity[1] if profile_identity is not None else None,
        )
    except Exception:
        subsystem.driver.shutdown()
        raise


def collect_sample_paths(sample_dir: Path | None) -> list[Path]:
    if sample_dir is None:
        return []
    return sorted([*sample_dir.glob("*.pgm"), *sample_dir.glob("*.ppm")])


def _validate_launch_options(options: LocalShellLaunchOptions) -> None:
    if options.source not in {"simulated", "hardware"}:
        raise LocalShellStartupError(f"Unsupported shell source '{options.source}'.")
    if options.source == "hardware" and options.sample_dir is not None:
        raise LocalShellStartupError("--sample-dir is only valid for --source simulated.")


def _build_subsystem(options: LocalShellLaunchOptions) -> CameraSubsystem:
    if options.source == "simulated":
        return build_simulated_camera_subsystem(
            sample_image_paths=collect_sample_paths(options.sample_dir),
            preview_poll_interval_seconds=options.poll_interval_seconds,
            shared_poll_interval_seconds=options.poll_interval_seconds,
        )
    return build_camera_subsystem(
        _create_hardware_driver(),
        preview_poll_interval_seconds=options.poll_interval_seconds,
        shared_poll_interval_seconds=options.poll_interval_seconds,
    )


def _create_hardware_driver():
    from vision_platform.integrations.camera.vimbax_camera_driver import VimbaXCameraDriver

    return VimbaXCameraDriver()


def _resolve_camera_id(options: LocalShellLaunchOptions) -> str | None:
    try:
        return resolve_camera_id(
            camera_id=options.camera_id,
            camera_alias=options.camera_alias,
        )
    except CameraAliasResolutionError as exc:
        raise LocalShellStartupError(str(exc)) from exc


def _apply_configuration_if_requested(
    controller,
    options: LocalShellLaunchOptions,
    initialized_status: CameraStatus,
) -> tuple[str, str] | None:
    override_request = ApplyConfigurationRequest(
        exposure_time_us=options.exposure_time_us,
        gain=options.gain,
        pixel_format=options.pixel_format,
        acquisition_frame_rate=options.acquisition_frame_rate,
        roi_offset_x=options.roi_offset_x,
        roi_offset_y=options.roi_offset_y,
        roi_width=options.roi_width,
        roi_height=options.roi_height,
    )
    profile_identity: tuple[str, str] | None = None
    effective_request = override_request

    if options.configuration_profile is not None:
        try:
            resolved_profile = resolve_camera_configuration_profile(
                profile_id=options.configuration_profile,
                camera_class=_resolve_profile_camera_class(options, initialized_status),
            )
        except CameraConfigurationProfileResolutionError as exc:
            raise LocalShellStartupError(str(exc)) from exc
        effective_request = merge_configuration_requests(resolved_profile.configuration, override_request)
        profile_identity = (resolved_profile.profile_id, resolved_profile.camera_class)

    if not has_configuration_values(effective_request):
        return profile_identity

    controller.apply_configuration(effective_request)
    return profile_identity


def _resolve_profile_camera_class(options: LocalShellLaunchOptions, initialized_status: CameraStatus) -> str:
    if options.profile_camera_class:
        return options.profile_camera_class
    if initialized_status.camera_model:
        return normalize_camera_class_name(initialized_status.camera_model)
    raise LocalShellStartupError(
        "Configuration profile resolution requires --profile-camera-class when the camera model is unavailable."
    )


__all__ = [
    "LocalShellLaunchOptions",
    "LocalShellSession",
    "LocalShellStartupError",
    "build_local_shell_session",
    "collect_sample_paths",
]
