from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class LocalShellSessionMetadata:
    session_id: str
    source: str
    camera_id: str | None
    configuration_profile_id: str | None
    state: str
    created_at: str
    session_directory: Path
    commands_file: Path
    status_file: Path
    closed_at: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> LocalShellSessionMetadata:
        return cls(
            session_id=str(payload["session_id"]),
            source=str(payload["source"]),
            camera_id=_optional_str(payload.get("camera_id")),
            configuration_profile_id=_optional_str(payload.get("configuration_profile_id")),
            state=str(payload["state"]),
            created_at=str(payload["created_at"]),
            session_directory=Path(payload["session_directory"]),
            commands_file=Path(payload["commands_file"]),
            status_file=Path(payload["status_file"]),
            closed_at=_optional_str(payload.get("closed_at")),
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "session_id": self.session_id,
            "source": self.source,
            "camera_id": self.camera_id,
            "configuration_profile_id": self.configuration_profile_id,
            "state": self.state,
            "created_at": self.created_at,
            "session_directory": self.session_directory,
            "commands_file": self.commands_file,
            "status_file": self.status_file,
        }
        if self.closed_at is not None:
            payload["closed_at"] = self.closed_at
        return payload


@dataclass(slots=True)
class LocalShellActiveSessionMetadata:
    session_id: str
    session_directory: Path
    source: str
    camera_id: str | None
    configuration_profile_id: str | None
    state: str
    updated_at: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> LocalShellActiveSessionMetadata:
        return cls(
            session_id=str(payload["session_id"]),
            session_directory=Path(payload["session_directory"]),
            source=str(payload["source"]),
            camera_id=_optional_str(payload.get("camera_id")),
            configuration_profile_id=_optional_str(payload.get("configuration_profile_id")),
            state=str(payload["state"]),
            updated_at=str(payload["updated_at"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "session_directory": self.session_directory,
            "source": self.source,
            "camera_id": self.camera_id,
            "configuration_profile_id": self.configuration_profile_id,
            "state": self.state,
            "updated_at": self.updated_at,
        }


@dataclass(slots=True)
class LocalShellLiveCommand:
    command_id: str
    command_name: str
    payload: dict[str, Any]
    created_at: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> LocalShellLiveCommand:
        return cls(
            command_id=str(payload["command_id"]),
            command_name=str(payload["command_name"]),
            payload=_dict_payload(payload.get("payload")),
            created_at=str(payload["created_at"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "command_name": self.command_name,
            "payload": self.payload,
            "created_at": self.created_at,
        }


@dataclass(slots=True)
class LocalShellLiveCommandResult:
    command_id: str
    command_name: str | None
    success: bool
    result: dict[str, Any] | None
    error: str | None
    updated_at: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> LocalShellLiveCommandResult:
        return cls(
            command_id=str(payload["command_id"]),
            command_name=_optional_str(payload.get("command_name")),
            success=bool(payload["success"]),
            result=_optional_dict_payload(payload.get("result")),
            error=_optional_str(payload.get("error")),
            updated_at=str(payload["updated_at"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "command_name": self.command_name,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "updated_at": self.updated_at,
        }


@dataclass(slots=True)
class LocalShellLiveStatusSnapshot:
    payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> LocalShellLiveStatusSnapshot:
        return cls(payload=_dict_payload(payload))

    def to_dict(self) -> dict[str, Any]:
        return dict(self.payload)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _dict_payload(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise TypeError("Protocol payload must be a dictionary.")
    return dict(value)


def _optional_dict_payload(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise TypeError("Protocol payload must be a dictionary.")
    return dict(value)


__all__ = [
    "LocalShellActiveSessionMetadata",
    "LocalShellLiveCommand",
    "LocalShellLiveCommandResult",
    "LocalShellLiveStatusSnapshot",
    "LocalShellSessionMetadata",
]
