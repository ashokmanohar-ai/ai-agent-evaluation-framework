from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    with source.open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if not isinstance(data, dict):
        raise ValueError(f"configuration root must be a mapping: {source}")
    return data


def load_tool_policy(path: str | Path) -> dict[str, dict[str, Any]]:
    data = load_yaml(path)
    tools = data.get("tools")
    if not isinstance(tools, dict) or not tools:
        raise ValueError("tool policy must define a non-empty tools mapping")
    normalized: dict[str, dict[str, Any]] = {}
    for name, policy in tools.items():
        if not isinstance(name, str) or not isinstance(policy, dict):
            raise ValueError("each tool policy must be a named mapping")
        normalized[name] = dict(policy)
    return normalized
