# 🏠 Panasonic Mirale Snart Home
> **An advanced, PhD-level Smart Home Orchestration System** powered by Local/NLP-driven LLM resolution, MQTT real-time control, and dynamic device capability mapping.

---

## 🚀 Overview
**MirAle System** is a modular **LLM-powered IoT control system** designed for **multi-room, multi-device smart homes**.  
It resolves **natural language commands** (including ambiguous ones) into **validated MQTT commands** using a **hybrid rule-first + LLM fallback approach**.

This system is designed to handle **complex device-capability mapping**, **real-time MQTT publishing**, and **LLM-based ambiguity resolution** — ideal for **job-level, production-grade deployments**.







## ✨ Key Features
- **Multi-Room, Multi-Device Support**  
  JSON-based device registry with full mapping of IDs, aliases, MQTT topics, and capabilities.

- **Advanced LLM Resolution Engine**  
  Hybrid parsing pipeline:
  1. **Rule-first NLP** (regex + semantic hints)  
  2. **LLM fallback** (for complex, multi-step or ambiguous commands)  
  3. **Clarification prompts** when confidence is low.

- **Real-Time MQTT Control**  
  Publish structured control messages (`/set/{capability}`) with QoS 1.

- **Dynamic Capability Validation**  
  Prevents invalid values (e.g., 200% brightness) by checking capability ranges.

- **Ambiguity Handling**  
  Interactive prompts for:
  - Missing device
  - Missing room
  - Missing action
  - Multiple matches

- **WebSocket Live Log**  
  Instant feedback of MQTT events in the browser.

---




**Components:**
- `llm/engine.py` — Intent parsing, ambiguity detection, clarification prompts.
- `registry/registry.py` — Device lookup, alias matching, capability validation.
- `mqtt/bridge.py` — MQTT publish/subscribe handler.
- `frontend/index.html` — Minimal web dashboard with live logs.
- `app.py` — FastAPI API + WebSocket server.

---

## 🧠 LLM Resolution Logic

**Example:**  
> `"Turn on the AC in the living room and set it to 23°C"`

Steps:
1. **Regex match** detects "turn on" → `power=true` and "23°C" → `targetTemperature=23`.
2. **Room match** finds `"living room"`.
3. **Device match** from registry finds `"Living Room AC"`.
4. **Capability validation** checks:
   - `power` is supported (bool)
   - `targetTemperature` is in range `[16, 30]`.
5. **MQTT Publish** →  
   - `home/livingroom/ac/set/power` → `true`  
   - `home/livingroom/ac/set/targetTemperature` → `23`

If missing info → LLM clarifies:  
> `"Which AC do you mean? Living room or bedroom?"`

## 🧠 How LLM Resolution Works

### Challenges
1. **Ambiguous commands** — e.g., "Turn it on" without specifying device/room.  
2. **Multi-device environments** — Matching user intent to correct device + room.
3. **Complex capability resolution** — e.g., "Set the bedroom AC to 23° and swing mode."  
4. **Fallback requirements** — When LLM is unavailable or fails.

### Solutions Implemented
- **Hybrid Parsing Pipeline**:
  1. **Rule-based**: Fast heuristics for clear commands.
  2. **LLM Enrichment**: When ambiguities exist, the system queries FLAN-T5 or optional OpenAI API for structured JSON output.
  3. **Fallback Recovery**: Regex + spaCy for minimal viable execution.

- **Structured Output Example**:
```json
{
  "intent": "turn_on",
  "device": "air_conditioner",
  "room": "bedroom",
  "params": { "temperature": 23, "mode": "cool" },
  "confidence": 0.87,
  "ambiguities": []
}
```

---

## 📡 MQTT Integration

**Topic Structure**:
```
home/<room>/<device>/set/<action>
home/<room>/<device>/status
```

**Example**:
- Command: `home/living_room/ac/set/temperature`
- Status: `home/living_room/ac/status`

**Features**:
- Bidirectional MQTT communication
- Real-time UI updates via WebSocket
- Automatic device-topic mapping from JSON registry

---

## 📂 Project Structure

```
IntelliHome-AI/
│── backend/
│   ├── app.py                  # FastAPI backend + WebSocket
│   ├── llm_engine.py           # LLM parser with hybrid logic
│   ├── mqtt_controller.py      # MQTT publish/subscribe handling
│   ├── device_registry.json    # Device-capability mapping
│   ├── logger.py               # Usage logging
│   ├── suggestions.py          # Smart command suggestions
│
│── frontend/
│   ├── index.html              # Web-based UI
│   ├── app.js                  # WebSocket communication
│
│── requirements.txt
│── docker-compose.yml
│── README.md
```

---

## 📈 Business Impact

| Business Value | Impact |
|----------------|--------|
| **User Experience** | Zero-learning-curve voice/text control with contextual reasoning |
| **Energy Efficiency** | Device usage optimization and predictive control reduces wastage |
| **Scalability** | Modular design allows new devices to be integrated in under 5 minutes |
| **Differentiation** | Combines LLM adaptability with IoT robustness for competitive advantage |

---

## 🔮 Future Roadmap

| Stage | Feature | Status |
|-------|---------|--------|
| 1 | GUI Dashboard | In Progress |
| 2 | Predictive AI Automations | Planned |
| 3 | Energy Optimization Engine | Planned |
| 4 | Multilingual Support Expansion | Planned |
| 5 | Edge Deployment | Planned |

---

## 🏁 Conclusion
**IntelliHome AI** represents a leap in smart home orchestration — combining **cutting-edge AI reasoning** with **real-time IoT control**.  
It’s designed for both **technical robustness** and **business scalability**, making it ideal for enterprise deployments.

