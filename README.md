# 🏠 Panasonic Mirale Snart Home
> **An advanced, PhD-level Smart Home Orchestration System** powered by Local/NLP-driven LLM resolution, MQTT real-time control, and dynamic device capability mapping.

---

## 🚀 Overview
**MirAle System** is a modular **LLM-powered IoT control system** designed for **multi-room, multi-device smart homes**.  
It resolves **natural language commands** (including ambiguous ones) into **validated MQTT commands** using a **hybrid rule-first + LLM fallback approach**.

This system is designed to handle **complex device-capability mapping**, **real-time MQTT publishing**, and **LLM-based ambiguity resolution** — ideal for **job-level, production-grade deployments**.

---

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

🏆 Credits
Developed during Panasonic Smart Appliance AI Internship — focusing on LLM-driven complexity resolution and real-time IoT control.

yaml
Copy
Edit

---

If you want, I can now **package all the runnable code + this README into a ZIP** so you can upload to GitHub and show your manager in one go.  
Do you want me to prepare that ZIP for you now?
