from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional


SaveDirectoryMode = Literal["append", "new_subdirectory"]


@dataclass(slots=True)
class SetSaveDirectoryRequest:
    base_directory: Path
    mode: SaveDirectoryMode = "append"
    subdirectory_name: Optional[str] = None

    def resolve_directory(self) -> Path:
        if self.mode == "append":
            return self.base_directory
        if self.mode == "new_subdirectory":
            if not self.subdirectory_name:
                raise ValueError("SetSaveDirectoryRequest.subdirectory_name is required for mode 'new_subdirectory'.")
            return self.base_directory / self.subdirectory_name
        raise ValueError(f"Unsupported save directory mode '{self.mode}'.")
