from __future__ import annotations

from vision_platform.imaging.opencv_adapter import OpenCvFrameAdapter
from vision_platform.services.stream_service.preview_service import PreviewService


class OpenCvPreviewWindow:
    """Optional OpenCV-backed preview window on top of PreviewService."""

    def __init__(
        self,
        preview_service: PreviewService,
        window_name: str = "Camera Preview",
        frame_adapter: OpenCvFrameAdapter | None = None,
        zoom_step: float = 1.5,
        min_zoom_scale: float = 0.05,
        max_zoom_scale: float = 8.0,
    ) -> None:
        self._preview_service = preview_service
        self._window_name = window_name
        self._frame_adapter = frame_adapter or OpenCvFrameAdapter()
        self._zoom_step = zoom_step
        self._min_zoom_scale = min_zoom_scale
        self._max_zoom_scale = max_zoom_scale
        self._fit_to_window = True
        self._manual_zoom_scale: float | None = None
        self._last_display_scale = 1.0
        self._window_created = False

    def render_latest_frame(self, delay_ms: int = 1) -> bool:
        return self.render_latest_frame_and_get_key(delay_ms=delay_ms) is not None

    def render_latest_frame_and_get_key(self, delay_ms: int = 1) -> int | None:
        frame = self._preview_service.get_latest_frame()
        if frame is None:
            return None

        self._ensure_window()
        if not self.is_open():
            return 27

        image = self._frame_adapter.to_image(frame)
        viewport_size = self._frame_adapter.get_window_image_size(self._window_name) or (frame.width, frame.height)
        display_scale = self._resolve_display_scale(frame.width, frame.height, viewport_size[0], viewport_size[1])
        self._last_display_scale = display_scale
        overlay_text = self._build_overlay_text()
        display_image = self._frame_adapter.render_into_viewport(
            image,
            viewport_width=viewport_size[0],
            viewport_height=viewport_size[1],
            scale=display_scale,
            overlay_text=overlay_text,
        )
        pressed_key = self._frame_adapter.show_image(self._window_name, display_image, delay_ms=delay_ms)
        self._handle_shortcuts(pressed_key)
        if not self.is_open():
            return 27
        return pressed_key

    @property
    def is_fit_to_window_enabled(self) -> bool:
        return self._fit_to_window

    @property
    def manual_zoom_scale(self) -> float | None:
        return self._manual_zoom_scale

    def zoom_in(self) -> None:
        base_scale = self._last_display_scale if self._fit_to_window or self._manual_zoom_scale is None else self._manual_zoom_scale
        self._manual_zoom_scale = min(base_scale * self._zoom_step, self._max_zoom_scale)
        self._fit_to_window = False

    def zoom_out(self) -> None:
        base_scale = self._last_display_scale if self._fit_to_window or self._manual_zoom_scale is None else self._manual_zoom_scale
        self._manual_zoom_scale = max(base_scale / self._zoom_step, self._min_zoom_scale)
        self._fit_to_window = False

    def enable_fit_to_window(self) -> None:
        self._fit_to_window = True
        self._manual_zoom_scale = None

    def close(self) -> None:
        if self._window_created:
            self._frame_adapter.destroy_window(self._window_name)
            self._window_created = False

    def is_open(self) -> bool:
        if not self._window_created:
            return False
        return self._frame_adapter.is_window_visible(self._window_name)

    def _ensure_window(self) -> None:
        if self._window_created:
            return
        self._frame_adapter.create_window(self._window_name)
        self._window_created = True

    def _resolve_display_scale(self, frame_width: int, frame_height: int, viewport_width: int, viewport_height: int) -> float:
        if self._fit_to_window:
            return max(min(viewport_width / frame_width, viewport_height / frame_height), self._min_zoom_scale)

        assert self._manual_zoom_scale is not None
        return self._manual_zoom_scale

    def _build_overlay_text(self) -> str:
        mode = "FIT" if self._fit_to_window else "ZOOM"
        return f"{mode} {self._last_display_scale:.2f}x | i=in o=out f=fit q=quit"

    def _handle_shortcuts(self, pressed_key: int) -> None:
        normalized_key = pressed_key & 0xFF
        if normalized_key in (ord("i"), ord("I")):
            self.zoom_in()
        elif normalized_key in (ord("o"), ord("O")):
            self.zoom_out()
        elif normalized_key in (ord("f"), ord("F")):
            self.enable_fit_to_window()


__all__ = ["OpenCvPreviewWindow"]
