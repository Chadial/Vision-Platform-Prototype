from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from vision_platform.services.companion_contract_service import build_failed_companion_command_result
from vision_platform.services.local_shell_command_execution_service import (
    LocalShellCompanionCommandExecutionContext,
    LocalShellCompanionCommandExecutionError,
    LocalShellCompanionCommandExecutionOutcome,
    execute_local_shell_companion_command,
)
from vision_platform.services.local_shell_runtime_tick_coordinator import LocalShellRuntimeTickCoordinator
from vision_platform.services.local_shell_session_protocol import LocalShellLiveCommand
from vision_platform.services.local_shell_session_service import LocalShellLiveSyncSession
from vision_platform.services.local_shell_status_projection_service import (
    LocalShellStatusProjectionInput,
    build_local_shell_live_command_result,
)


@dataclass(slots=True)
class LocalShellCompanionFacade:
    runtime_tick_coordinator: LocalShellRuntimeTickCoordinator = field(default_factory=LocalShellRuntimeTickCoordinator)

    @property
    def processed_count(self) -> int:
        return self.runtime_tick_coordinator.processed_count

    @processed_count.setter
    def processed_count(self, value: int) -> None:
        self.runtime_tick_coordinator.processed_count = value

    def run_timer_tick(
        self,
        *,
        session: LocalShellLiveSyncSession | None,
        execute_command: Callable[[LocalShellLiveCommand], dict[str, Any]],
        build_failed_result: Callable[[LocalShellLiveCommand, Exception], dict[str, Any] | None],
        request_refresh: Callable[[], None],
    ) -> None:
        self.runtime_tick_coordinator.run_timer_tick(
            session=session,
            execute_command=execute_command,
            build_failed_result=build_failed_result,
            request_refresh=request_refresh,
        )

    def poll_commands(
        self,
        *,
        session: LocalShellLiveSyncSession | None,
        execute_command: Callable[[LocalShellLiveCommand], dict[str, Any]],
        build_failed_result: Callable[[LocalShellLiveCommand, Exception], dict[str, Any] | None],
    ) -> None:
        self.runtime_tick_coordinator.poll_commands(
            session=session,
            execute_command=execute_command,
            build_failed_result=build_failed_result,
        )

    def publish_status(
        self,
        *,
        session: LocalShellLiveSyncSession | None,
        projection: LocalShellStatusProjectionInput,
    ) -> None:
        self.runtime_tick_coordinator.publish_status(
            session=session,
            projection=projection,
        )

    def execute_command(
        self,
        *,
        command: LocalShellLiveCommand,
        build_execution_context: Callable[[], LocalShellCompanionCommandExecutionContext],
        apply_outcome: Callable[[LocalShellCompanionCommandExecutionOutcome], None],
        build_result: Callable[[str, Any], dict[str, Any]],
    ) -> dict[str, Any]:
        try:
            outcome = execute_local_shell_companion_command(
                command,
                context=build_execution_context(),
            )
        except LocalShellCompanionCommandExecutionError as exc:
            apply_outcome(exc.outcome)
            raise RuntimeError(str(exc)) from exc
        apply_outcome(outcome)
        return build_result(command.command_name, outcome.result)

    @staticmethod
    def build_live_command_result(
        *,
        command_name: str,
        result: Any,
        status_projection: LocalShellStatusProjectionInput,
        selected_save_directory,
    ) -> dict[str, Any]:
        return build_local_shell_live_command_result(
            command_name=command_name,
            result=result,
            status_projection=status_projection,
            selected_save_directory=selected_save_directory,
        )

    @staticmethod
    def build_failed_command_result(
        *,
        command_name: str,
        failure_reflection: dict[str, object | None] | None,
    ) -> dict[str, object | None]:
        return build_failed_companion_command_result(
            command_name=command_name,
            failure_reflection=failure_reflection,
        )


__all__ = ["LocalShellCompanionFacade"]
