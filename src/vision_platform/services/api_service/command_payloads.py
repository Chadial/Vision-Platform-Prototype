from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from vision_platform.models import SubsystemStatus
from vision_platform.services.api_service.status_payloads import ApiSubsystemStatusPayload, map_subsystem_status_to_api_payload


@dataclass(slots=True)
class ApiCommandErrorPayload:
    code: str
    message: str
    details: dict[str, Any] | None = None


@dataclass(slots=True)
class ApiCommandEnvelopePayload:
    success: bool
    command: str | None
    source: str | None
    result: Any
    status: ApiSubsystemStatusPayload | None
    error: ApiCommandErrorPayload | None


def build_success_command_payload(
    *,
    command: str,
    source: str,
    result: Any,
    status: SubsystemStatus,
) -> ApiCommandEnvelopePayload:
    return ApiCommandEnvelopePayload(
        success=True,
        command=command,
        source=source,
        result=result,
        status=map_subsystem_status_to_api_payload(status),
        error=None,
    )


def build_error_command_payload(
    *,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> ApiCommandEnvelopePayload:
    return ApiCommandEnvelopePayload(
        success=False,
        command=None,
        source=None,
        result=None,
        status=None,
        error=ApiCommandErrorPayload(
            code=code,
            message=message,
            details=details,
        ),
    )


__all__ = [
    "ApiCommandEnvelopePayload",
    "ApiCommandErrorPayload",
    "build_error_command_payload",
    "build_success_command_payload",
]
