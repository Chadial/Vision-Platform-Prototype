"""Optional imaging compatibility shim for the legacy camera_app namespace."""

__all__ = ["OpenCvFrameAdapter", "OpenCvPreviewWindow"]


def __getattr__(name: str):
    if name == "OpenCvFrameAdapter":
        from vision_platform.imaging import OpenCvFrameAdapter

        return OpenCvFrameAdapter
    if name == "OpenCvPreviewWindow":
        from vision_platform.imaging import OpenCvPreviewWindow

        return OpenCvPreviewWindow
    raise AttributeError(name)
