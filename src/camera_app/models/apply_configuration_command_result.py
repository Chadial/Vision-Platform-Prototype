from dataclasses import dataclass

from camera_app.models.camera_configuration import CameraConfiguration


@dataclass(slots=True)
class ApplyConfigurationCommandResult:
    applied_configuration: CameraConfiguration

    @classmethod
    def from_applied_configuration(
        cls,
        configuration: CameraConfiguration,
    ) -> "ApplyConfigurationCommandResult":
        return cls(applied_configuration=configuration)
