from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SnapshotCommandResult:
    saved_path: Path
