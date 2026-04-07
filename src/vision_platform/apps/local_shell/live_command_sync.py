from __future__ import annotations

import json
from dataclasses import asdict, dataclass, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import sleep
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class LocalShellLiveSyncSession:
    session_id: str
    root_directory: Path
    session_directory: Path
    session_file: Path
    active_session_file: Path
    commands_file: Path
    results_directory: Path
    status_file: Path


@dataclass(slots=True)
class LocalShellLiveCommand:
    command_id: str
    command_name: str
    payload: dict[str, Any]
    created_at: str


class LocalShellLiveSyncError(Exception):
    pass


def create_live_sync_session(
    *,
    root_directory: Path,
    source: str,
    camera_id: str | None,
    configuration_profile_id: str | None,
) -> LocalShellLiveSyncSession:
    root_directory.mkdir(parents=True, exist_ok=True)
    session_id = _build_session_id()
    session_directory = root_directory / session_id
    results_directory = session_directory / "results"
    session_directory.mkdir(parents=True, exist_ok=True)
    results_directory.mkdir(parents=True, exist_ok=True)

    session = LocalShellLiveSyncSession(
        session_id=session_id,
        root_directory=root_directory,
        session_directory=session_directory,
        session_file=session_directory / "session.json",
        active_session_file=root_directory / "active_session.json",
        commands_file=session_directory / "commands.jsonl",
        results_directory=results_directory,
        status_file=session_directory / "status.json",
    )
    write_json(
        session.session_file,
        {
            "session_id": session.session_id,
            "source": source,
            "camera_id": camera_id,
            "configuration_profile_id": configuration_profile_id,
            "state": "running",
            "created_at": _utc_now(),
            "session_directory": session.session_directory,
            "commands_file": session.commands_file,
            "status_file": session.status_file,
        },
    )
    write_json(
        session.active_session_file,
        {
            "session_id": session.session_id,
            "session_directory": session.session_directory,
            "source": source,
            "camera_id": camera_id,
            "configuration_profile_id": configuration_profile_id,
            "state": "running",
            "updated_at": _utc_now(),
        },
    )
    session.commands_file.touch(exist_ok=True)
    return session


def resolve_active_live_sync_session(root_directory: Path) -> LocalShellLiveSyncSession:
    active_session_file = root_directory / "active_session.json"
    if not active_session_file.exists():
        raise LocalShellLiveSyncError("No active wx shell session is registered.")
    active_payload = read_json(active_session_file)
    session_directory = Path(active_payload["session_directory"])
    session = LocalShellLiveSyncSession(
        session_id=active_payload["session_id"],
        root_directory=root_directory,
        session_directory=session_directory,
        session_file=session_directory / "session.json",
        active_session_file=active_session_file,
        commands_file=session_directory / "commands.jsonl",
        results_directory=session_directory / "results",
        status_file=session_directory / "status.json",
    )
    session_payload = read_json(session.session_file)
    if session_payload.get("state") != "running":
        raise LocalShellLiveSyncError("The active wx shell session is not running anymore.")
    return session


def close_live_sync_session(session: LocalShellLiveSyncSession) -> None:
    payload = read_json(session.session_file)
    payload["state"] = "closed"
    payload["closed_at"] = _utc_now()
    write_json(session.session_file, payload)
    if session.active_session_file.exists():
        active_payload = read_json(session.active_session_file)
        if active_payload.get("session_id") == session.session_id:
            session.active_session_file.unlink()


def append_live_command(
    session: LocalShellLiveSyncSession,
    *,
    command_name: str,
    payload: dict[str, Any] | None = None,
) -> LocalShellLiveCommand:
    command = LocalShellLiveCommand(
        command_id=uuid4().hex,
        command_name=command_name,
        payload=payload or {},
        created_at=_utc_now(),
    )
    line = json.dumps(to_serializable(asdict(command)), sort_keys=True)
    with session.commands_file.open("a", encoding="utf-8") as handle:
        handle.write(f"{line}\n")
    return command


def read_pending_live_commands(
    session: LocalShellLiveSyncSession,
    *,
    processed_count: int,
) -> tuple[list[LocalShellLiveCommand], int]:
    if not session.commands_file.exists():
        return [], processed_count
    lines = session.commands_file.read_text(encoding="utf-8").splitlines()
    pending_lines = lines[processed_count:]
    commands = [
        LocalShellLiveCommand(
            command_id=payload["command_id"],
            command_name=payload["command_name"],
            payload=payload.get("payload", {}),
            created_at=payload["created_at"],
        )
        for payload in (json.loads(line) for line in pending_lines if line.strip())
    ]
    return commands, len(lines)


def write_live_command_result(
    session: LocalShellLiveSyncSession,
    *,
    command_id: str,
    success: bool,
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> Path:
    result_path = session.results_directory / f"{command_id}.json"
    write_json(
        result_path,
        {
            "command_id": command_id,
            "success": success,
            "result": result,
            "error": error,
            "updated_at": _utc_now(),
        },
    )
    return result_path


def wait_for_live_command_result(
    session: LocalShellLiveSyncSession,
    *,
    command_id: str,
    timeout_seconds: float = 5.0,
    poll_interval_seconds: float = 0.05,
) -> dict[str, Any]:
    result_path = session.results_directory / f"{command_id}.json"
    elapsed = 0.0
    while elapsed <= timeout_seconds:
        if result_path.exists():
            return read_json(result_path)
        sleep(poll_interval_seconds)
        elapsed += poll_interval_seconds
    raise LocalShellLiveSyncError(f"Timed out waiting for wx shell command result '{command_id}'.")


def write_live_status_snapshot(session: LocalShellLiveSyncSession, payload: dict[str, Any]) -> None:
    write_json(session.status_file, payload)
    if session.active_session_file.exists():
        active_payload = read_json(session.active_session_file)
        if active_payload.get("session_id") == session.session_id:
            active_payload["updated_at"] = _utc_now()
            active_payload["state"] = "running"
            write_json(session.active_session_file, active_payload)


def read_live_status_snapshot(session: LocalShellLiveSyncSession) -> dict[str, Any]:
    if not session.status_file.exists():
        raise LocalShellLiveSyncError("The active wx shell has not published a status snapshot yet.")
    return read_json(session.status_file)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_serializable(payload), indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def to_serializable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value):
        return {key: to_serializable(item) for key, item in asdict(value).items()}
    if hasattr(value, "__dict__"):
        return {str(key): to_serializable(item) for key, item in vars(value).items()}
    if isinstance(value, dict):
        return {str(key): to_serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_serializable(item) for item in value]
    return value


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _build_session_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + f"-{uuid4().hex[:8]}"


__all__ = [
    "LocalShellLiveCommand",
    "LocalShellLiveSyncError",
    "LocalShellLiveSyncSession",
    "append_live_command",
    "close_live_sync_session",
    "create_live_sync_session",
    "read_live_status_snapshot",
    "read_pending_live_commands",
    "resolve_active_live_sync_session",
    "to_serializable",
    "wait_for_live_command_result",
    "write_live_command_result",
    "write_live_status_snapshot",
]
