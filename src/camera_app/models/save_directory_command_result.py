from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class SaveDirectoryCommandResult:
    selected_directory: Optional[Path]
    was_cleared: bool = False

    @classmethod
    def selected(cls, directory: Path) -> "SaveDirectoryCommandResult":
        return cls(selected_directory=directory, was_cleared=False)

    @classmethod
    def cleared(cls) -> "SaveDirectoryCommandResult":
        return cls(selected_directory=None, was_cleared=True)
