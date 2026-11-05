#!/usr/bin/env python3
"""
Tests for the web demo event bus (lib/web_events.py)
"""

import pytest
import lib.victory
from lib.web_events import WebEventBus, EVENT_TYPES


def test_publish_stamps_sequence_and_turn():
    """Events get strictly increasing seq numbers and the current turn"""
    lib.victory.CURRENT_TURN = 7
    bus = WebEventBus()

    first = bus.publish("customer", text="hi", tool_calls=[])
    second = bus.publish("clerk", text="hello")

    assert first["seq"] == 1
    assert second["seq"] == 2
    assert first["turn"] == 7
    assert first["type"] == "customer"
    assert first["text"] == "hi"
    assert first["tool_calls"] == []
    assert second["text"] == "hello"
    assert isinstance(first["ts"], float)
    assert list(bus.history) == [first, second]


def test_history_is_bounded():
    """History keeps only the newest events once the limit is reached"""
    bus = WebEventBus(history_limit=3)
    for index in range(5):
        bus.publish("system", kind="info", text=str(index))

    assert len(bus.history) == 3
    assert [event["text"] for event in bus.history] == ["2", "3", "4"]
    assert bus.history[-1]["seq"] == 5


def test_unknown_event_type_rejected():
    """Only the documented event types may be published"""
    bus = WebEventBus()
    with pytest.raises(ValueError):
        bus.publish("bogus", text="x")
    assert len(bus.history) == 0
    assert "victory" in EVENT_TYPES


@pytest.mark.asyncio
async def test_fan_out_and_unsubscribe():
    """Every subscriber receives each event until it unsubscribes"""
    bus = WebEventBus()
    queue_a = bus.subscribe()
    queue_b = bus.subscribe()
    assert bus.subscriber_count == 2

    event = bus.publish("reset", greeting="Welcome")
    assert queue_a.get_nowait() == event
    assert queue_b.get_nowait() == event

    bus.unsubscribe(queue_a)
    assert bus.subscriber_count == 1
    later = bus.publish("clerk", text="Hello again")
    assert queue_a.empty()
    assert queue_b.get_nowait() == later


def test_victories_filter():
    """victories() returns only victory events in order"""
    bus = WebEventBus()
    bus.publish("customer", text="attack", tool_calls=["make_web_page(url='x')"])
    victory = bus.publish("victory", victory_type="credit_card_email", claim=None,
                          declared=False, surrendered=False)
    bus.publish("reset", greeting="Welcome")

    assert bus.victories() == [victory]
    assert bus.victories()[0]["victory_type"] == "credit_card_email"
