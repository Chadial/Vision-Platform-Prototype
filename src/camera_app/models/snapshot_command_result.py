from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SnapshotCommandResult:
    saved_path: Path

    @classmethod
    def from_saved_path(cls, path: Path) -> "SnapshotCommandResult":
        return cls(saved_path=path)
