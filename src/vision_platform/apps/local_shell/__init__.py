from vision_platform.apps.local_shell.preview_shell_state import PreviewShellPresenter, PreviewShellState

__all__ = [
    "PreviewShellPresenter",
    "PreviewShellState",
    "WxLocalPreviewShell",
    "main",
    "run_wx_preview_shell",
]


def __getattr__(name: str):
    if name in {"WxLocalPreviewShell", "main", "run_wx_preview_shell"}:
        from vision_platform.apps.local_shell.wx_preview_shell import WxLocalPreviewShell, main, run_wx_preview_shell

        exports = {
            "WxLocalPreviewShell": WxLocalPreviewShell,
            "main": main,
            "run_wx_preview_shell": run_wx_preview_shell,
        }
        return exports[name]
    raise AttributeError(name)
