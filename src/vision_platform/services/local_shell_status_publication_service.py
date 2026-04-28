from __future__ import annotations

from vision_platform.services.local_shell_session_service import (
    LocalShellLiveSyncSession,
    write_live_status_snapshot,
)
from vision_platform.services.local_shell_status_projection_service import (
    LocalShellStatusProjectionInput,
    build_local_shell_status_snapshot,
)


def publish_local_shell_status_snapshot(
    *,
    session: LocalShellLiveSyncSession,
    projection: LocalShellStatusProjectionInput,
) -> None:
    write_live_status_snapshot(
        session,
        build_local_shell_status_snapshot(projection),
    )


__all__ = ["publish_local_shell_status_snapshot"]
