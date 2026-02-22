# Author: Aditya Dogra
from __future__ import annotations

"""Local JSON subscription storage.

Control flow:
1) Load/create storage document.
2) Mutate user WG subscriptions.
3) Save and list flattened subscription records.
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

DEFAULT_DB = Path.home() / ".ietf_wg_agent_subscriptions.json"


@dataclass(frozen=True)
class Subscription:
    user_id: str
    acronym: str


def _load(path: Path = DEFAULT_DB) -> dict[str, Any]:
    # Section 1: Read existing database or create default structure.
    if not path.exists():
        return {"users": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _save(data: dict[str, Any], path: Path = DEFAULT_DB) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def register_daily_update(user_id: str, acronym: str, path: Path = DEFAULT_DB) -> None:
    # Section 2: Upsert user and acronym with deduplication.
    data = _load(path)
    users = data.setdefault("users", {})
    user = users.setdefault(user_id, {"wgs": []})

    wgs: list[str] = user.setdefault("wgs", [])
    ac = acronym.lower()
    if ac not in wgs:
        wgs.append(ac)
        wgs.sort()
    _save(data, path)


def list_subscriptions(path: Path = DEFAULT_DB) -> list[Subscription]:
    # Section 3: Flatten persisted mapping into typed objects.
    data = _load(path)
    users = data.get("users", {})

    out: list[Subscription] = []
    for user_id, payload in users.items():
        for acronym in payload.get("wgs", []):
            out.append(Subscription(user_id=user_id, acronym=acronym))
    return out
