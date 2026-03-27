from __future__ import annotations

import argparse
from pathlib import Path

from camera_app.logging.log_service import configure_logging
from vision_platform.integrations.camera.capability_probe import write_camera_capabilities_json


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export a normalized camera capability profile to JSON.")
    parser.add_argument(
        "--camera-id",
        default=None,
        help="Optional explicit camera id. If omitted, the first available camera is used.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        required=True,
        help="Target JSON file path for the exported capability profile.",
    )
    return parser


def main() -> int:
    configure_logging()
    parser = _build_argument_parser()
    args = parser.parse_args()
    output_path = write_camera_capabilities_json(
        output_path=args.output_path,
        camera_id=args.camera_id,
    )
    print(output_path)
    return 0


__all__ = ["main"]
