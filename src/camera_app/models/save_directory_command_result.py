from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class SaveDirectoryCommandResult:
    selected_directory: Optional[Path]
    was_cleared: bool = False
