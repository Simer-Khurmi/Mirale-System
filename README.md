# 🏠 Panasonic Mirale Snart Home
> **An advanced, PhD-level Smart Home Orchestration System** powered by Local/NLP-driven LLM resolution, MQTT real-time control, and dynamic device capability mapping.

---

## 🚀 Overview
**MirAle System** is a modular **LLM-powered IoT control system** designed for **multi-room, multi-device smart homes**.  
It resolves **natural language commands** (including ambiguous ones) into **validated MQTT commands** using a **hybrid rule-first + LLM fallback approach**.

This system is designed to handle **complex device-capability mapping**, **real-time MQTT publishing**, and **LLM-based ambiguity resolution** — ideal for **job-level, production-grade deployments**.

---
## 📂 Folder Structure


├─ backend/
│  ├─ app.py                  # FastAPI server (REST + WebSocket)
│  ├─ orchestrator.py         # LLM agent: parse → plan → explain
│  ├─ validators.py           # hard constraints, schema & safety
│  ├─ planner.py              # multi-device planning, exceptions
│  ├─ mqtt_io.py              # MQTT pub/sub, correlation, retries
│  ├─ state.py                # shadow state, ledger, rollback
│  ├─ registry.py             # device/capability graph
│  ├─ prompts.py              # system & critique prompts
│  └─ config.py               # settings loader
├─ data/
│  ├─ devices.schema.json     # capability schema
│  ├─ devices.sample.json     # example inventory
│  └─ synonyms.json           # alias & fuzzy matching support
├─ tests/
│  ├─ test_end_to_end.py
│  └─ fixtures/
├─ docs/
│  └─ architecture.mmd        # mermaid diagram source
├─ docker/
│  ├─ Dockerfile
│  └─ docker-compose.yml
├─ requirements.txt
├─ .env.example
└─ README.md

flowchart LR
A[User Utterance\n(text/voice)] --> B[FastAPI /gateway]
B --> C[LLM Orchestrator\n(intent + entities + plan)]
C --> D[Constraint Validator\n(rules + schema + firmware gates)]
D --> E[Planner\n(device graph & exceptions)]
E --> F[Dry-Run Simulator\nshadow state]
F -->|Plan OK| G[MQTT Publisher\nQoS1 + correlation]
G --> H[(MQTT Broker)]
H --> I[Edge Devices]
I --> J[Status/ACK]
J --> K[State Tracker\nShadow + Ledger]
K --> L[Resolution Engine\nsuccess/rollback]
L --> M[User Feedback\nexplanations + next steps]
C --> N[(Vector/Alias Memory)]
E --> O[(Device Registry\ncapability map)]


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

## 🏗 Architecture

[User Command]
│
▼
┌──────────────┐
│ LLM Resolver │ ← Hybrid: Regex + Semantic Parsing + GPT fallback
└──────┬───────┘
│ Parsed Intent
▼
┌──────────────┐
│ Device Match │ ← Finds candidates from JSON registry
└──────┬───────┘
│ Validated Capability & Value
▼
┌──────────────┐
│ MQTT Bridge │ ← Publishes structured command to broker
└──────┬───────┘
│
▼
[IoT Device Receives Command]
│
▼
[Device Action + Status Feedback]

markdown
Copy
Edit

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

---

## 📂 Project Structure
.
├── app.py # FastAPI entry point
├── frontend/ # Minimal UI + WS log
├── llm/engine.py # Parsing engine
├── mqtt/bridge.py # MQTT bridge
├── registry/devices.json # Device registry
├── registry/registry.py # Lookup & validation
├── telemetry/bus.py # WebSocket log bus
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example

yaml
Copy
Edit

---

## ⚙️ Setup & Run

### 1️⃣ Clone & Install
```bash
git clone https://github.com/YOUR_USERNAME/intellihome-ai.git
cd intellihome-ai
cp .env.example .env
2️⃣ Docker (Recommended)
bash
Copy
Edit
docker compose up --build
UI → http://localhost:8080

API Docs → http://localhost:8000/docs

3️⃣ Local (Without Docker)
bash
Copy
Edit
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
Requires Mosquitto broker running locally.

💡 Demo Ideas
Try in UI:

"Set bedroom AC to 24 degrees"

"Dim living room lights to 20%"

"Open living room curtains"

"Movie mode in living room"

🛠 Future Enhancements
Voice input via WebRTC

Scene orchestration (“Party mode” triggers multiple devices)

Cloud-to-local fallback

Federated LLM fine-tuning on usage logs

# IntelliHome AI — Advanced LLM-Driven Smart Home Automation

## Overview
**IntelliHome AI** is a next-generation, AI-powered smart home orchestration system developed as part of an advanced internship project.  
It combines **LLM-powered natural language understanding**, **real-time MQTT-based device control**, **multi-device capability mapping**, and **multi-user contextual reasoning** to deliver seamless, reliable, and highly intelligent home automation.

This system has been designed for **job-level production readiness** while maintaining **research-grade novelty** suitable for journal publication.

---

## 🚀 Key Features

| Category                | Features |
|------------------------|----------|
| **Natural Language Understanding** | LLM-powered command parsing with FLAN-T5 + fallback heuristics, ambiguity detection, multilingual (EN/FR) |
| **Device Control**     | Real-time MQTT publishing & subscribing, topic auto-mapping, multi-device/room capability mapping |
| **User Context**       | Multi-user sessions, personalized command history, smart suggestions based on usage |
| **Resilience**         | Rule-based fallback parsing, regex & spaCy recovery if LLM fails, structured error handling |
| **Data Handling**      | JSON-based device registry, CLI & WebSocket logging, CSV export for analysis |
| **Extensibility**      | Modular architecture, new device capability integration in under 5 minutes |
| **Future Scope**       | GUI dashboard, AI-driven automation routines, predictive energy optimization |

---

## 🏗 System Architecture

```mermaid
flowchart TD
    User[User Command - Voice/Text] --> |Speech-to-Text| Input[Command Input Handler]
    Input --> LLMParser[LLM Command Parser (FLAN-T5 + Fallback Heuristics)]
    LLMParser --> Validation[Context & Capability Validation]
    Validation --> MQTT[MQTT Controller]
    MQTT --> Device[IoT Device Execution]
    Device --> MQTTStatus[Device Status Updates]
    MQTTStatus --> Logger[Usage Logger + Analytics]
    Logger --> Suggestions[Smart Command Suggestions]
    Suggestions --> User
    subgraph Data Layer
        Mapping[Device-Capability Mapping JSON]
        Logs[Usage Logs CSV/DB]
    end
    LLMParser --> Mapping
    Logger --> Logs
```

---

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

