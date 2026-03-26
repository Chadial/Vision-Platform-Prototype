"""IDE-friendly package shim for the src-based camera_app package."""

from pathlib import Path


_PACKAGE_DIR = Path(__file__).resolve().parent
_SRC_PACKAGE_DIR = _PACKAGE_DIR.parent / "src" / "camera_app"

__path__ = [str(_PACKAGE_DIR)]
if _SRC_PACKAGE_DIR.is_dir():
    __path__.append(str(_SRC_PACKAGE_DIR))
