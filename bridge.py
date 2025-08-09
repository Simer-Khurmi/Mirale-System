import os, json, asyncio
from typing import Optional, Dict, Any
import paho.mqtt.client as mqtt
from pydantic import BaseModel
from ..telemetry.bus import EventBus, Event
from ..registry.registry import DeviceRegistry

class MqttEvent(BaseModel):
    topic: str
    payload: Dict[str, Any]

class MqttBridge:
    def __init__(self, registry: DeviceRegistry, bus: EventBus):
        self.host = os.getenv("MQTT_BROKER_HOST", "localhost")
        self.port = int(os.getenv("MQTT_BROKER_PORT", "1883"))
        self.username = os.getenv("MQTT_USERNAME") or None
        self.password = os.getenv("MQTT_PASSWORD") or None
        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self.registry = registry
        self.bus = bus
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        if self.username:
            self._client.username_pw_set(self.username, self.password or "")
        self._client.connect(self.host, self.port, 60)
        self._task = asyncio.create_task(self._loop())
        # Subscribe to all status topics from registry prefix
        for t in self.registry.status_topics():
            self._client.subscribe(t, qos=1)

    async def stop(self):
        if self._task:
            self._task.cancel()
        self._client.disconnect()

    async def publish_command(self, topic: str, payload: Dict[str, Any]):
        self._client.publish(topic, json.dumps(payload), qos=1, retain=False)
        await self.bus.emit(Event(type="mqtt_out", payload={"topic": topic, "payload": payload}))

    # Internal loop
    async def _loop(self):
        while True:
            self._client.loop(timeout=0.1)
            await asyncio.sleep(0.01)

    # Callbacks
    def _on_connect(self, client, userdata, flags, rc):
        # Connected
        pass

    def _on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except Exception:
            data = {"raw": msg.payload.decode("utf-8", errors="ignore")}
        asyncio.create_task(self.bus.emit(Event(type="mqtt_in", payload={"topic": msg.topic, "payload": data})))
