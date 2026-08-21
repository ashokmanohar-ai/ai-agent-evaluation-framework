from __future__ import annotations

from collections.abc import Callable
from typing import Any


def get_ticket(ticket_id: str) -> dict[str, str]:
    return {"ticket_id": ticket_id, "status": "OPEN"}


def get_service_status(service: str) -> dict[str, str]:
    return {"service": service, "status": "OPERATIONAL"}


def lookup_policy(policy: str) -> dict[str, str]:
    return {"policy": policy, "answer": "Refunds are available within 30 days."}


SAFE_TOOL_ALLOWLIST: dict[str, Callable[..., dict[str, Any]]] = {
    "get_ticket": get_ticket,
    "get_service_status": get_service_status,
    "lookup_policy": lookup_policy,
}
