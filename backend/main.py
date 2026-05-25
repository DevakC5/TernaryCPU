"""FastAPI WebSocket server for TernaryCPU Web Visualizer."""

import asyncio
import json
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.snapshot_engine import SnapshotEngine


# ── Global engine ─────────────────────────────────────────────────────
engine = SnapshotEngine(memory_size=10000, realistic_timing=True)
ws_clients: set[WebSocket] = set()
broadcast_task = None


# ── Pydantic models ───────────────────────────────────────────────────
class LoadProgramRequest(BaseModel):
    source: str


class StepRequest(BaseModel):
    count: int = 1


# ── Lifecycle ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global broadcast_task
    broadcast_task = asyncio.create_task(_broadcast_loop())
    yield
    broadcast_task.cancel()


app = FastAPI(title="TernaryCPU Web Visualizer", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── WebSocket ─────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    ws_clients.add(ws)
    try:
        # Send initial state
        snap = engine.capture()
        await ws.send_json({"type": "snapshot", "data": snap.to_json()})
        await ws.send_json({"type": "status", "data": {"connected": True, "mode": "realistic_timing"}})
        # Send demos on connect
        demos = _get_demos()
        await ws.send_json({"type": "demos", "data": demos})

        # Handle incoming commands
        async for message in ws.iter_json():
            msg_type = message.get("type", "")
            if msg_type == "load":
                result = engine.load_program(message.get("source", ""))
                await ws.send_json({"type": "load_result", "data": result})
                snap = engine.capture()
                await ws.send_json({"type": "snapshot", "data": snap.to_json()})

            elif msg_type == "step":
                count = message.get("count", 1)
                snaps = engine.step(count)
                for s in snaps:
                    await ws.send_json({"type": "snapshot", "data": s.to_json()})

            elif msg_type == "run":
                snaps = engine.run_to_halt()
                for s in snaps:
                    await ws.send_json({"type": "snapshot", "data": s.to_json()})

            elif msg_type == "reset":
                engine.reset()
                snap = engine.capture()
                await ws.send_json({"type": "snapshot", "data": snap.to_json()})

            elif msg_type == "get_default_demo":
                demos = _get_demos()
                await ws.send_json({"type": "demos", "data": demos})

    except WebSocketDisconnect:
        pass
    finally:
        ws_clients.discard(ws)


async def _broadcast_loop():
    """Periodically broadcast state to all connected clients."""
    while True:
        await asyncio.sleep(0.05)  # 20fps broadcast
        if ws_clients and not engine.cpu.halted:
            snap = engine.capture()
            payload = {"type": "snapshot", "data": snap.to_json()}
            dead = set()
            for ws in ws_clients:
                try:
                    await ws.send_json(payload)
                except Exception:
                    dead.add(ws)
            ws_clients -= dead


# ── REST endpoints ────────────────────────────────────────────────────
@app.get("/api/status")
def get_status():
    return {
        "status": "ok",
        "clients": len(ws_clients),
        "cycle": engine.cpu.cycles,
        "halted": engine.cpu.halted,
        "pc": engine.cpu.pc,
        "realistic_timing": engine.cpu.realistic_timing,
    }


@app.post("/api/load")
def load_program(req: LoadProgramRequest):
    result = engine.load_program(req.source)
    return result


@app.post("/api/step")
def step_cpu(req: StepRequest):
    snaps = engine.step(req.count)
    return {"snapshots": [s.to_json() for s in snaps]}


@app.post("/api/run")
def run_cpu():
    snaps = engine.run_to_halt()
    return {"snapshots": [s.to_json() for s in snaps]}


@app.post("/api/reset")
def reset_cpu():
    engine.reset()
    snap = engine.capture()
    return {"snapshot": snap.to_json()}


@app.get("/api/snapshot")
def get_snapshot():
    snap = engine.capture()
    return snap.to_json()


@app.get("/api/demos")
def get_demos():
    return _get_demos()


def _get_demos():
    from trinary.ui.demos import DEMOS
    return [{"name": k, "source": v} for k, v in DEMOS.items()]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
