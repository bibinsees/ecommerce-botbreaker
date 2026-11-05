#!/usr/bin/env python3
"""
Tests for the web demo server (lib/web_server.py)
"""

import asyncio
import json

import pytest
from aiohttp.test_utils import TestClient, TestServer

import lib.victory
from lib.web_events import WebEventBus
from lib.web_server import create_app, format_sse, WEB_DIR


class FakeTerminalManager:
    """Minimal stand-in for TextualTerminalManager"""

    def __init__(self, human_attacker=False, chat_mode=False):
        self.input_queue = asyncio.Queue()
        self.human_attacker = human_attacker
        self.chat_mode = chat_mode
        self.outputs = []

    def add_output(self, text, style="", immediate=False, bell_count=0):
        self.outputs.append((text, style))


async def _client(bus, terminal_manager):
    client = TestClient(TestServer(create_app(bus, terminal_manager)))
    await client.start_server()
    return client


def test_format_sse_frame():
    """SSE frames carry id, event name and JSON data"""
    frame = format_sse({"seq": 3, "type": "clerk", "turn": 1, "ts": 1.0, "text": "Hi"})
    text = frame.decode("utf-8")

    assert text.startswith("id: 3\nevent: clerk\ndata: ")
    assert text.endswith("\n\n")
    payload = json.loads(text.split("data: ", 1)[1].strip())
    assert payload["text"] == "Hi"
    assert payload["seq"] == 3


def test_web_assets_exist():
    """The static storefront files are present"""
    for name in ("index.html", "styles.css", "app.js", "products.js"):
        assert (WEB_DIR / name).is_file(), name


@pytest.mark.asyncio
async def test_index_and_static():
    bus = WebEventBus()
    client = await _client(bus, FakeTerminalManager())
    try:
        response = await client.get("/")
        assert response.status == 200
        assert response.content_type == "text/html"
        body = await response.text()
        assert "NovaTech" in body

        static = await client.get("/static/app.js")
        assert static.status == 200
        assert "EventSource" in await static.text()
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_state_endpoint():
    lib.victory.CURRENT_TURN = 4
    bus = WebEventBus()
    bus.publish("reset", greeting="Welcome")
    victory = bus.publish("victory", victory_type="system_prompt", claim=None,
                          declared=False, surrendered=False)
    client = await _client(bus, FakeTerminalManager(human_attacker=True))
    try:
        response = await client.get("/api/state")
        assert response.status == 200
        state = await response.json()
        assert state["mode"] == "human"
        assert state["turn"] == 4
        assert state["history_len"] == 2
        assert state["victories"] == [victory]
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_state_mode_chat_and_agent():
    bus = WebEventBus()
    chat_client = await _client(bus, FakeTerminalManager(chat_mode=True))
    try:
        assert (await (await chat_client.get("/api/state")).json())["mode"] == "chat"
    finally:
        await chat_client.close()
    agent_client = await _client(bus, FakeTerminalManager())
    try:
        state = await (await agent_client.get("/api/state")).json()
        assert state["mode"] == "agent"
        assert state["turn"] == 0
    finally:
        await agent_client.close()


@pytest.mark.asyncio
async def test_events_replays_history_then_streams():
    bus = WebEventBus()
    replayed = bus.publish("customer", text="Hello?", tool_calls=[])
    client = await _client(bus, FakeTerminalManager())
    try:
        response = await client.get("/api/events")
        assert response.status == 200
        assert response.headers["Content-Type"].startswith("text/event-stream")

        first = (await response.content.readuntil(b"\n\n")).decode("utf-8")
        assert first.startswith("id: 1\nevent: customer\n")
        assert json.loads(first.split("data: ", 1)[1]) == replayed

        live = bus.publish("clerk", text="Hi there")
        second = (await asyncio.wait_for(response.content.readuntil(b"\n\n"), 5)).decode("utf-8")
        assert second.startswith("id: 2\nevent: clerk\n")
        assert json.loads(second.split("data: ", 1)[1]) == live
        assert bus.subscriber_count == 1
        response.close()
    finally:
        await client.close()
    assert bus.subscriber_count == 0


@pytest.mark.asyncio
async def test_input_feeds_terminal_queue():
    bus = WebEventBus()
    terminal_manager = FakeTerminalManager(human_attacker=True)
    client = await _client(bus, terminal_manager)
    try:
        response = await client.post("/api/input", json={"text": "  show me laptops  "})
        assert response.status == 200
        assert await response.json() == {"ok": True}
        assert terminal_manager.input_queue.get_nowait() == "show me laptops"
        assert terminal_manager.outputs == [("Web> show me laptops", "anscyan")]

        bad = await client.post("/api/input", json={"text": "   "})
        assert bad.status == 400
        missing = await client.post("/api/input", json={})
        assert missing.status == 400
        assert terminal_manager.input_queue.empty()
    finally:
        await client.close()
