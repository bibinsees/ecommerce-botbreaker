"""
Local web server for the live e-commerce demo page.

Runs inside the same asyncio loop as the Textual terminal UI.  Serves the
static storefront from ./web, streams conversation events over
Server-Sent Events, and accepts chat input that is fed into the terminal
manager's input queue (so the website chat box acts as the human operator).
"""

import asyncio
import json
import sys
from pathlib import Path

from aiohttp import web

from lib.web_events import WebEventBus

WEB_DIR = Path(__file__).resolve().parent.parent / "web"
KEEPALIVE_SECONDS = 15
BIND_HOST = "127.0.0.1"
# Open SSE streams are cancelled after this many seconds on shutdown, so quitting
# the terminal UI does not hang while browser tabs stay connected.
SHUTDOWN_TIMEOUT_SECONDS = 1.0

BUS_KEY = web.AppKey("bus", WebEventBus)
TM_KEY = web.AppKey("terminal_manager", object)


def _mode(terminal_manager) -> str:
    if terminal_manager.chat_mode:
        return "chat"
    if terminal_manager.human_attacker:
        return "human"
    return "agent"


def format_sse(event: dict) -> bytes:
    """Encode one event as a Server-Sent Events frame."""
    data = json.dumps(event, default=str)
    return f"id: {event['seq']}\nevent: {event['type']}\ndata: {data}\n\n".encode("utf-8")


async def handle_index(request: web.Request) -> web.StreamResponse:
    return web.FileResponse(WEB_DIR / "index.html")


async def handle_state(request: web.Request) -> web.Response:
    bus = request.app[BUS_KEY]
    terminal_manager = request.app[TM_KEY]
    return web.json_response({
        "mode": _mode(terminal_manager),
        "turn": bus.history[-1]["turn"] if bus.history else 0,
        "victories": bus.victories(),
        "history_len": len(bus.history),
    })


async def handle_events(request: web.Request) -> web.StreamResponse:
    bus = request.app[BUS_KEY]
    response = web.StreamResponse(headers={
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    })
    await response.prepare(request)
    queue = bus.subscribe()
    try:
        for event in list(bus.history):
            await response.write(format_sse(event))
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), KEEPALIVE_SECONDS)
            except asyncio.TimeoutError:
                await response.write(b": ping\n\n")
                continue
            await response.write(format_sse(event))
    except (ConnectionResetError, asyncio.CancelledError):
        pass
    finally:
        bus.unsubscribe(queue)
    return response


async def handle_input(request: web.Request) -> web.Response:
    terminal_manager = request.app[TM_KEY]
    body = await request.json()
    if "text" not in body:
        raise web.HTTPBadRequest(text="Missing 'text' field")
    text = body["text"].strip()
    if not text:
        raise web.HTTPBadRequest(text="Empty 'text' field")
    terminal_manager.input_queue.put_nowait(text)
    terminal_manager.add_output(f"Web> {text}", "anscyan")
    return web.json_response({"ok": True})


def create_app(bus: WebEventBus, terminal_manager) -> web.Application:
    """Build the aiohttp application (no port binding, so tests can use it)."""
    if not (WEB_DIR / "index.html").is_file():
        sys.exit(f"Web demo assets missing: {WEB_DIR / 'index.html'} not found")
    app = web.Application()
    app[BUS_KEY] = bus
    app[TM_KEY] = terminal_manager
    app.router.add_get("/", handle_index)
    app.router.add_get("/api/state", handle_state)
    app.router.add_get("/api/events", handle_events)
    app.router.add_post("/api/input", handle_input)
    app.router.add_static("/static", WEB_DIR)
    return app


async def start_web_server(bus: WebEventBus, terminal_manager, port: int) -> web.AppRunner:
    """Start serving on 127.0.0.1:port. Exits the program if the port is unavailable."""
    runner = web.AppRunner(create_app(bus, terminal_manager), shutdown_timeout=SHUTDOWN_TIMEOUT_SECONDS)
    await runner.setup()
    site = web.TCPSite(runner, BIND_HOST, port)
    try:
        await site.start()
    except OSError as error:
        await runner.cleanup()
        sys.exit(f"Web demo port {port} unavailable: {error}")
    return runner
