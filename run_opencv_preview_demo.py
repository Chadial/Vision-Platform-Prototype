from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from camera_app.smoke.opencv_preview_demo import run_opencv_preview_demo


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the optional OpenCV preview demo with the simulated driver.")
    parser.add_argument(
        "--sample-dir",
        type=Path,
        default=None,
        help="Optional directory containing .pgm or .ppm sample images.",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        type=float,
        default=0.03,
        help="Preview polling interval in seconds.",
    )
    parser.add_argument(
        "--frame-limit",
        type=int,
        default=None,
        help="Optional number of rendered frames before the demo exits.",
    )
    args = parser.parse_args()

    result = run_opencv_preview_demo(
        sample_dir=args.sample_dir,
        poll_interval_seconds=args.poll_interval_seconds,
        frame_limit=args.frame_limit,
    )
    print(f"Rendered {result.rendered_frames} frames.")


if __name__ == "__main__":
    main()
