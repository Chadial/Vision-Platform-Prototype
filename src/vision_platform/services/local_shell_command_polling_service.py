from __future__ import annotations

from collections.abc import Callable
from typing import Any

from vision_platform.services.local_shell_session_service import (
    LocalShellLiveCommand,
    LocalShellLiveSyncSession,
    read_pending_live_commands,
    write_live_command_result,
)


def poll_local_shell_live_commands(
    *,
    session: LocalShellLiveSyncSession,
    processed_count: int,
    execute_command: Callable[[LocalShellLiveCommand], dict[str, Any]],
    build_failed_result: Callable[[LocalShellLiveCommand, Exception], dict[str, Any] | None],
) -> int:
    commands, next_processed_count = read_pending_live_commands(
        session,
        processed_count=processed_count,
    )
    for command in commands:
        try:
            result = execute_command(command)
        except Exception as exc:
            write_live_command_result(
                session,
                command_id=command.command_id,
                success=False,
                command_name=command.command_name,
                result=build_failed_result(command, exc),
                error=str(exc),
            )
            continue
        write_live_command_result(
            session,
            command_id=command.command_id,
            success=True,
            command_name=command.command_name,
            result=result,
        )
    return next_processed_count


__all__ = ["poll_local_shell_live_commands"]
