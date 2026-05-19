from __future__ import annotations

import inspect

from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

EnterpriseHook = Callable[[dict[str, Any]], Awaitable[None] | None]


class EnterpriseEventBus:
    """Async in-process event bus for enterprise/workspace lifecycle hooks."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EnterpriseHook]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: EnterpriseHook) -> None:
        if handler not in self._subscribers[event_name]:
            self._subscribers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: EnterpriseHook) -> None:
        if handler in self._subscribers[event_name]:
            self._subscribers[event_name].remove(handler)

    async def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        for handler in list(self._subscribers[event_name]):
            result = handler(dict(payload))
            if inspect.isawaitable(result):
                await result


enterprise_event_bus = EnterpriseEventBus()
