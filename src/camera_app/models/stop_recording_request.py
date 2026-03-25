from dataclasses import dataclass


@dataclass(slots=True)
class StopRecordingRequest:
    reason: str = "external_request"
