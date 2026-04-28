from __future__ import annotations

from dataclasses import dataclass


FailureReflectionPayload = dict[str, object | None]


@dataclass(slots=True)
class LocalShellFailureReflectionState:
    _current: FailureReflectionPayload | None = None

    def set_failure(self, *, source: str, action: str, message: str, external: bool) -> None:
        self._current = {
            "phase": "failed",
            "source": source,
            "action": action,
            "message": message,
            "external": external,
        }

    def clear_for_source(self, source: str) -> None:
        if self._current is not None and self._current.get("source") == source:
            self._current = None

    def snapshot(self) -> FailureReflectionPayload | None:
        if self._current is None:
            return None
        return dict(self._current)


__all__ = [
    "FailureReflectionPayload",
    "LocalShellFailureReflectionState",
]
