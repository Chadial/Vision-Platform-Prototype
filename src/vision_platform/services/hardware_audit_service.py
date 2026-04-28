from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from vision_platform.models import CameraStatus
from vision_platform.models import IntervalCaptureStatus
from vision_platform.models import RecordingStatus
from vision_platform.models import SubsystemStatus


@dataclass(slots=True)
class HardwareAuditEntry:
    timestamp_utc: str
    severity: str
    category: str
    event: str
    message: str
    stage: str | None = None
    source_kind: str | None = None
    camera_id: str | None = None
    camera_name: str | None = None
    camera_model: str | None = None
    camera_serial: str | None = None
    details: dict[str, str] = field(default_factory=dict)


class HardwareAuditService:
    """Append-only hardware audit sink for warnings, degraded states, and incidents."""

    def __init__(self, audit_log_path: Path | None = None) -> None:
        self._audit_log_path = audit_log_path
        self._last_status_signatures: dict[str, tuple[Any, ...]] = {}

    @property
    def audit_log_path(self) -> Path | None:
        return self._audit_log_path

    def record_camera_status(self, *, stage: str, status: CameraStatus) -> bool:
        severity, event, message, details = self._classify_camera_status(status)
        if severity is None:
            return False
        return self._record_status_like(
            stage=stage,
            status=status,
            severity=severity,
            category="camera",
            event=event,
            message=message,
            details=details,
        )

    def record_subsystem_status(self, *, stage: str, status: SubsystemStatus) -> bool:
        severity, event, message, details = self._classify_subsystem_status(status)
        if severity is None:
            return False
        return self._record_status_like(
            stage=stage,
            status=status,
            severity=severity,
            category="subsystem",
            event=event,
            message=message,
            details=details,
        )

    def record_incident(
        self,
        *,
        stage: str,
        severity: str,
        event: str,
        message: str,
        status: CameraStatus | SubsystemStatus | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self._append_entry(
            HardwareAuditEntry(
                timestamp_utc=self._now(),
                severity=severity,
                category="incident",
                event=event,
                message=message,
                stage=stage,
                details=self._normalize_details(details or {}),
                **self._status_identity(status),
            )
        )

    def record_exception(
        self,
        *,
        stage: str,
        exc: Exception,
        status: CameraStatus | SubsystemStatus | None = None,
        severity: str = "error",
        event: str = "exception",
        details: dict[str, Any] | None = None,
    ) -> None:
        payload = dict(details or {})
        payload["exception_type"] = exc.__class__.__name__
        self.record_incident(
            stage=stage,
            severity=severity,
            event=event,
            message=str(exc) or exc.__class__.__name__,
            status=status,
            details=payload,
        )

    def _record_status_like(
        self,
        *,
        stage: str,
        status: CameraStatus | SubsystemStatus,
        severity: str,
        category: str,
        event: str,
        message: str,
        details: dict[str, Any],
    ) -> bool:
        signature = self._build_signature(status)
        if self._last_status_signatures.get(stage) == signature:
            return False
        self._last_status_signatures[stage] = signature
        self._append_entry(
            HardwareAuditEntry(
                timestamp_utc=self._now(),
                severity=severity,
                category=category,
                event=event,
                message=message,
                stage=stage,
                details=self._normalize_details(details),
                **self._status_identity(status),
            )
        )
        return True

    def _classify_camera_status(self, status: CameraStatus) -> tuple[str | None, str, str, dict[str, Any]]:
        details: dict[str, Any] = {}
        if status.source_kind != "hardware":
            return None, "camera_ok", "camera status is nominal", details
        if not status.is_initialized:
            return (
                "warning",
                "camera_not_initialized",
                "camera is not initialized",
                details,
            )
        if status.capability_probe_error:
            details["capability_probe_error"] = status.capability_probe_error
            return (
                "warning",
                "capability_probe_warning",
                "camera capability probe reported a non-blocking warning",
                details,
            )
        if status.last_error:
            details["last_error"] = status.last_error
            return (
                "error",
                "camera_error",
                "camera reported an error",
                details,
            )
        if status.source_kind == "hardware" and not status.capabilities_available:
            return (
                "warning",
                "capabilities_unavailable",
                "hardware camera capabilities are not currently available",
                details,
            )
        return None, "camera_ok", "camera status is nominal", details

    def _classify_subsystem_status(
        self,
        status: SubsystemStatus,
    ) -> tuple[str | None, str, str, dict[str, Any]]:
        if status.camera.source_kind != "hardware":
            return None, "subsystem_ok", "subsystem status is nominal", {}
        camera_severity, camera_event, camera_message, details = self._classify_camera_status(status.camera)
        if camera_severity is not None:
            return camera_severity, camera_event, camera_message, details

        if status.recording.last_error:
            details["recording_last_error"] = status.recording.last_error
            return (
                "error",
                "recording_error",
                "recording status reported an error",
                details,
            )
        if status.interval_capture.last_error:
            details["interval_capture_last_error"] = status.interval_capture.last_error
            return (
                "warning",
                "interval_capture_warning",
                "interval capture reported a warning",
                details,
            )
        return None, "subsystem_ok", "subsystem status is nominal", details

    def _status_identity(self, status: CameraStatus | SubsystemStatus | None) -> dict[str, str | None]:
        camera_status = status.camera if isinstance(status, SubsystemStatus) else status
        if camera_status is None:
            return {
                "source_kind": None,
                "camera_id": None,
                "camera_name": None,
                "camera_model": None,
                "camera_serial": None,
            }
        return {
            "source_kind": camera_status.source_kind,
            "camera_id": camera_status.camera_id,
            "camera_name": camera_status.camera_name,
            "camera_model": camera_status.camera_model,
            "camera_serial": camera_status.camera_serial,
        }

    def _build_signature(self, status: CameraStatus | SubsystemStatus) -> tuple[Any, ...]:
        if isinstance(status, SubsystemStatus):
            return (
                status.camera.is_initialized,
                status.camera.is_acquiring,
                status.camera.source_kind,
                status.camera.camera_id,
                status.camera.capabilities_available,
                status.camera.capability_probe_error,
                status.camera.last_error,
                status.recording.is_recording,
                status.recording.frames_written,
                status.recording.dropped_frames,
                status.recording.last_error,
                status.interval_capture.is_capturing,
                status.interval_capture.frames_written,
                status.interval_capture.skipped_intervals,
                status.interval_capture.last_error,
            )
        return (
            status.is_initialized,
            status.is_acquiring,
            status.source_kind,
            status.camera_id,
            status.capabilities_available,
            status.capability_probe_error,
            status.last_error,
        )

    def _append_entry(self, entry: HardwareAuditEntry) -> None:
        if self._audit_log_path is None:
            return
        self._audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self._entry_to_dict(entry), ensure_ascii=False, sort_keys=True)
        with self._audit_log_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.write("\n")

    @staticmethod
    def _entry_to_dict(entry: HardwareAuditEntry) -> dict[str, Any]:
        return {
            "timestamp_utc": entry.timestamp_utc,
            "severity": entry.severity,
            "category": entry.category,
            "event": entry.event,
            "message": entry.message,
            "stage": entry.stage,
            "source_kind": entry.source_kind,
            "camera_id": entry.camera_id,
            "camera_name": entry.camera_name,
            "camera_model": entry.camera_model,
            "camera_serial": entry.camera_serial,
            "details": entry.details,
        }

    @staticmethod
    def _normalize_details(details: dict[str, Any]) -> dict[str, str]:
        normalized: dict[str, str] = {}
        for key, value in details.items():
            if value is None:
                continue
            normalized[key] = str(value)
        return normalized

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()


__all__ = ["HardwareAuditEntry", "HardwareAuditService"]
