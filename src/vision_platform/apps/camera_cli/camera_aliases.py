from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CAMERA_ALIAS_CONFIG_PATH = Path(__file__).resolve().parents[4] / "configs" / "camera_aliases.json"


@dataclass(slots=True)
class CameraAliasResolutionError(Exception):
    message: str
    details: dict[str, object] | None = None

    def __str__(self) -> str:
        return self.message


def resolve_camera_id(
    *,
    camera_id: str | None,
    camera_alias: str | None,
    config_path: Path = DEFAULT_CAMERA_ALIAS_CONFIG_PATH,
) -> str | None:
    if camera_id is not None and camera_alias is not None:
        raise CameraAliasResolutionError(
            "Specify either --camera-id or --camera-alias, not both.",
            details={
                "camera_id": camera_id,
                "camera_alias": camera_alias,
            },
        )

    if camera_alias is None:
        return camera_id

    aliases = load_camera_aliases(config_path)
    resolved_camera_id = aliases.get(camera_alias)
    if resolved_camera_id is None:
        raise CameraAliasResolutionError(
            f"Camera alias '{camera_alias}' is not defined in '{config_path}'.",
            details={
                "camera_alias": camera_alias,
                "config_path": str(config_path),
                "available_aliases": sorted(aliases.keys()),
            },
        )
    return resolved_camera_id


def load_camera_aliases(config_path: Path = DEFAULT_CAMERA_ALIAS_CONFIG_PATH) -> dict[str, str]:
    if not config_path.exists():
        raise CameraAliasResolutionError(
            f"Camera alias config '{config_path}' does not exist.",
            details={"config_path": str(config_path)},
        )

    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CameraAliasResolutionError(
            f"Camera alias config '{config_path}' is not valid JSON.",
            details={
                "config_path": str(config_path),
                "line": exc.lineno,
                "column": exc.colno,
            },
        ) from exc

    aliases = payload.get("aliases")
    if not isinstance(aliases, dict):
        raise CameraAliasResolutionError(
            f"Camera alias config '{config_path}' must contain an 'aliases' object.",
            details={"config_path": str(config_path)},
        )

    normalized_aliases: dict[str, str] = {}
    for alias, resolved_camera_id in aliases.items():
        if not isinstance(alias, str) or not alias.strip():
            raise CameraAliasResolutionError(
                f"Camera alias config '{config_path}' contains an invalid alias key.",
                details={"config_path": str(config_path)},
            )
        if not isinstance(resolved_camera_id, str) or not resolved_camera_id.strip():
            raise CameraAliasResolutionError(
                f"Camera alias '{alias}' in '{config_path}' must resolve to a non-empty camera id.",
                details={
                    "config_path": str(config_path),
                    "camera_alias": alias,
                },
            )
        normalized_aliases[alias.strip()] = resolved_camera_id.strip()

    return normalized_aliases


__all__ = [
    "CameraAliasResolutionError",
    "DEFAULT_CAMERA_ALIAS_CONFIG_PATH",
    "load_camera_aliases",
    "resolve_camera_id",
]
