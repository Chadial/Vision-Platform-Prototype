from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

from camera_app.validation.request_validation import validate_save_directory_request


SaveDirectoryMode = Literal["append", "new_subdirectory"]


@dataclass(slots=True)
class SetSaveDirectoryRequest:
    base_directory: Path
    mode: SaveDirectoryMode = "append"
    subdirectory_name: Optional[str] = None

    def resolve_directory(self) -> Path:
        validate_save_directory_request(self)
        if self.mode == "append":
            return self.base_directory
        if self.mode == "new_subdirectory":
            return self.base_directory / self.subdirectory_name
        raise ValueError(f"Unsupported save directory mode '{self.mode}'.")
