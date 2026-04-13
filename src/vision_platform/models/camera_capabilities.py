from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CapabilityState:
    supported: bool
    currently_available: bool
    currently_enabled: bool


@dataclass(frozen=True, slots=True)
class CameraCapabilities:
    capability_profile_available: bool
    capability_probe_warning: str | None
    exposure_time_control: CapabilityState
    gain_control: CapabilityState
    pixel_format_control: CapabilityState
    acquisition_frame_rate_control: CapabilityState
    roi_control: CapabilityState
    snapshot: CapabilityState
    recording: CapabilityState
    interval_capture: CapabilityState

