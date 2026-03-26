"""Optional imaging adapters exposed through the platform namespace."""

__all__ = ["OpenCvFrameAdapter", "OpenCvPreviewWindow"]


def __getattr__(name: str):
    if name == "OpenCvFrameAdapter":
        from vision_platform.imaging.opencv_adapter import OpenCvFrameAdapter

        return OpenCvFrameAdapter
    if name == "OpenCvPreviewWindow":
        from vision_platform.imaging.opencv_preview import OpenCvPreviewWindow

        return OpenCvPreviewWindow
    raise AttributeError(name)
