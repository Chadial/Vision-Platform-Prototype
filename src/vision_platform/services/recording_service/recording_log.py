from __future__ import annotations

import csv
from pathlib import Path
from typing import TextIO

RECORDING_LOG_FILENAME = "recording_log.csv"
RECORDING_LOG_HEADER = [
    "image_name",
    "frame_id",
    "camera_timestamp",
    "system_timestamp_utc",
]


def build_recording_log_path(save_directory: Path) -> Path:
    if save_directory is None:
        raise ValueError("save_directory must be set before resolving a recording log path.")
    return save_directory / RECORDING_LOG_FILENAME


def open_recording_log(path: Path, *, create_directories: bool) -> tuple[TextIO, csv.writer, bool]:
    if create_directories:
        path.parent.mkdir(parents=True, exist_ok=True)
    is_new_log = not path.exists() or path.stat().st_size == 0
    handle = path.open("a", newline="", encoding="utf-8")
    writer = csv.writer(handle)
    if is_new_log:
        writer.writerow(RECORDING_LOG_HEADER)
        handle.flush()
    return handle, writer, is_new_log


def append_recording_log_row(
    writer: csv.writer,
    handle: TextIO,
    *,
    image_name: str,
    frame_id: int | str | None,
    camera_timestamp: str | int | None,
    system_timestamp_utc: str,
) -> None:
    writer.writerow([image_name, frame_id, camera_timestamp, system_timestamp_utc])
    handle.flush()


def load_recording_log_image_names(path: Path) -> list[str]:
    if not path.exists():
        return []
    image_names: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("# "):
            continue
        row = next(csv.reader([line]), None)
        if row and row[0] != "image_name":
            image_names.append(row[0])
    return image_names
