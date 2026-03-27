from __future__ import annotations


class CoordinateExportService:
    """Formats selected image coordinates for reuse across different UI frontends."""

    def format_point(self, x: int, y: int) -> str:
        return f"x={x}, y={y}"


__all__ = ["CoordinateExportService"]
