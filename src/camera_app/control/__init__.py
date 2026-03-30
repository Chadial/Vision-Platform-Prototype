"""Host-facing command-surface compatibility shim for the legacy camera_app namespace."""

__all__ = ["CommandController"]


def __getattr__(name: str):
    if name == "CommandController":
        from vision_platform.control import CommandController

        return CommandController
    raise AttributeError(name)

