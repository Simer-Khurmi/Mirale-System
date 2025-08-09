from typing import Dict, Any, List
from pydantic import BaseModel

class Command(BaseModel):
    device_id: str
    action: str
    params: Dict[str, Any] = {}

class DeviceRegistry:
    def __init__(self):
        # Preload a multi-device map with capabilities and MQTT topics
        self._devices: Dict[str, Dict[str, Any]] = {
            "ac_living_001": {
                "name": "Living Room AC Pro",
                "type": "air_conditioner",
                "room": "living room",
                "topic": "home/livingroom/ac",
                "capabilities": ["power","temperature","mode","fan","swing","timer","energy"]
            },
            "ac_bedroom_001": {
                "name": "Master Bedroom AC Ultra",
                "type": "air_conditioner",
                "room": "bedroom",
                "topic": "home/bedroom/ac",
                "capabilities": ["power","temperature","mode","fan","swing","timer","energy"]
            },
            "light_living_001": {
                "name": "Living Room Smart Lights",
                "type": "light",
                "room": "living room",
                "topic": "home/livingroom/lights",
                "capabilities": ["power","brightness","color","scene","energy"]
            },
            "curtain_living_001": {
                "name": "Living Room Smart Curtains",
                "type": "curtain",
                "room": "living room",
                "topic": "home/livingroom/curtains",
                "capabilities": ["position","open","close"]
            },
            "security_main_001": {
                "name": "Main Security System",
                "type": "security",
                "room": "main",
                "topic": "home/security/main",
                "capabilities": ["arming","mode","zones","notify"]
            }
        }

    def list_devices(self) -> List[Dict[str, Any]]:
        return [{"id": i, **d} for i, d in self._devices.items()]

    def status_topics(self) -> List[str]:
        # Subscribe to status topics for each device
        return [f"{d['topic']}/status" for d in self._devices.values()]

    def resolve_command(self, cmd: Command) -> Dict[str, Any]:
        d = self._devices.get(cmd.device_id)
        if not d:
            raise ValueError("Unknown device_id")
        # Map logical actions -> MQTT payloads
        action = cmd.action.lower()
        topic = f"{d['topic']}/set/{action}"
        payload = {"action": action, **cmd.params}
        return {"topic": topic, "payload": payload}
