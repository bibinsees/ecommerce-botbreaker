"""
In-process event bus for the live web demo.

The orchestrator (botbreaker.py) publishes typed events describing the
conversation between the RedTeamAgent and the SalesAgent.  The web server
(lib/web_server.py) replays the history to new browser tabs and streams
new events to connected ones.  This module has no web dependencies.
"""

import asyncio
import time
from collections import deque

import lib.victory

HISTORY_LIMIT = 5000

EVENT_TYPES = ("customer", "clerk", "thoughts", "system", "victory", "reset")


class WebEventBus:
    """Bounded event history plus fan-out to subscriber queues."""

    def __init__(self, history_limit: int = HISTORY_LIMIT):
        self.history: deque = deque(maxlen=history_limit)
        self._subscribers: set[asyncio.Queue] = set()
        self._seq = 0

    def publish(self, event_type: str, **payload) -> dict:
        """Stamp, store and fan out one event. Returns the stored event."""
        if event_type not in EVENT_TYPES:
            raise ValueError(f"Unknown web event type: {event_type}")
        self._seq += 1
        event = {
            "seq": self._seq,
            "ts": time.time(),
            "turn": lib.victory.CURRENT_TURN,
            "type": event_type,
            **payload,
        }
        self.history.append(event)
        for queue in list(self._subscribers):
            queue.put_nowait(event)
        return event

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        self._subscribers.discard(queue)

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)

    def victories(self) -> list:
        return [event for event in self.history if event["type"] == "victory"]
