from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class SetSaveDirectoryResult:
    selected_directory: Optional[Path]
    was_cleared: bool = False
