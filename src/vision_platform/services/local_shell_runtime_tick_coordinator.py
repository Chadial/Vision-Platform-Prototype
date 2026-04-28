from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from vision_platform.services.local_shell_command_polling_service import poll_local_shell_live_commands
from vision_platform.services.local_shell_session_protocol import LocalShellLiveCommand
from vision_platform.services.local_shell_session_service import LocalShellLiveSyncSession
from vision_platform.services.local_shell_status_projection_service import LocalShellStatusProjectionInput
from vision_platform.services.local_shell_status_publication_service import publish_local_shell_status_snapshot


@dataclass(slots=True)
class LocalShellRuntimeTickCoordinator:
    processed_count: int = 0

    def poll_commands(
        self,
        *,
        session: LocalShellLiveSyncSession | None,
        execute_command: Callable[[LocalShellLiveCommand], dict[str, Any]],
        build_failed_result: Callable[[LocalShellLiveCommand, Exception], dict[str, Any] | None],
    ) -> None:
        if session is None:
            return
        self.processed_count = poll_local_shell_live_commands(
            session=session,
            processed_count=self.processed_count,
            execute_command=execute_command,
            build_failed_result=build_failed_result,
        )

    def publish_status(
        self,
        *,
        session: LocalShellLiveSyncSession | None,
        projection: LocalShellStatusProjectionInput,
    ) -> None:
        if session is None:
            return
        publish_local_shell_status_snapshot(
            session=session,
            projection=projection,
        )

    def run_timer_tick(
        self,
        *,
        session: LocalShellLiveSyncSession | None,
        execute_command: Callable[[LocalShellLiveCommand], dict[str, Any]],
        build_failed_result: Callable[[LocalShellLiveCommand, Exception], dict[str, Any] | None],
        request_refresh: Callable[[], None],
    ) -> None:
        self.poll_commands(
            session=session,
            execute_command=execute_command,
            build_failed_result=build_failed_result,
        )
        request_refresh()


__all__ = ["LocalShellRuntimeTickCoordinator"]
