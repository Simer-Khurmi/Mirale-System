import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

from .mqtt.bridge import MqttBridge, MqttEvent
from .llm.engine import LLMEngine
from .registry.registry import DeviceRegistry, Command
from .telemetry.bus import EventBus

app = FastAPI(title="IntelliHome AI", version="1.0.0")

# CORS
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:8000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global singletons
bus = EventBus()
registry = DeviceRegistry()
llm = LLMEngine()
mqtt = MqttBridge(registry=registry, bus=bus)

class ParseRequest(BaseModel):
    text: str
    lang: Optional[str] = None

class ParseResponse(BaseModel):
    intent: str
    action: str
    device: Optional[str] = None
    room: Optional[str] = None
    params: Dict[str, Any] = {}
    confidence: float
    ambiguities: List[str] = []

class CommandRequest(BaseModel):
    device_id: str
    action: str
    params: Dict[str, Any] = {}

@app.on_event("startup")
async def on_startup():
    await mqtt.start()

@app.on_event("shutdown")
async def on_shutdown():
    await mqtt.stop()

@app.get("/api/devices")
async def get_devices():
    return registry.list_devices()

@app.post("/api/parse", response_model=ParseResponse)
async def parse(req: ParseRequest):
    parsed = await llm.parse(req.text, lang_hint=req.lang)
    return parsed

@app.post("/api/command")
async def command(cmd: CommandRequest):
    resolved = registry.resolve_command(Command(**cmd.model_dump()))
    # publish to MQTT
    await mqtt.publish_command(resolved["topic"], resolved["payload"])
    return {"status": "queued", "topic": resolved["topic"], "payload": resolved["payload"]}

@app.get("/api/logs")
async def get_logs(limit: int = 200):
    return bus.tail(limit=limit)

# Serve frontend (static demo UI)
app.mount("/", StaticFiles(directory="src/frontend", html=True), name="frontend")

# ---- WebSocket for realtime updates ----
class WSManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, data: Dict[str, Any]):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except WebSocketDisconnect:
                dead.append(ws)
        for d in dead:
            self.disconnect(d)

ws_manager = WSManager()

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# Subscribe to MQTT events -> forward to websocket & logs
@bus.subscribe
async def on_mqtt_event(evt: MqttEvent):
    await ws_manager.broadcast({"type": "mqtt", "data": evt.model_dump()})
