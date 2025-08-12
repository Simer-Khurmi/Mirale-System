# 🏠 Panasonic Mirale Snart Home
> **An advanced System** powered by Local/NLP-driven LLM resolution, MQTT real-time control, and dynamic device capability mapping.

---

## 🚀 Overview
**MirAle System** is a modular **LLM-powered IoT control system** designed for **multi-room, multi-device smart homes**.  
It resolves **natural language commands** (including ambiguous ones) into **validated MQTT commands** using a **hybrid rule-first + LLM fallback approach**.

This system is designed to handle **complex device-capability mapping**, **real-time MQTT publishing**, and **LLM-based ambiguity resolution** — ideal for **job-level, production-grade deployments**.
![ChatGPT Image Aug 9, 2025, 04_17_12 PM](https://github.com/user-attachments/assets/c72af9cb-7127-4a02-b790-c025d501c4a6)

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
Got it — here’s a clear, technical, end-to-end flow for how the **LLM Resolution Agent** handles messy user requests, disambiguates devices, and safely executes commands over MQTT. This is implementation-ready logic you can hand to engineers.

# LLM Resolution: Technical Flow (Agent Perspective)

## 0) Roles & Micro-components

* **Gateway**: Receives user input (text/voice), attaches metadata (user, locale, room, time).
* **Normalizer**: Cleans text, expands abbreviations, corrects spelling.
* **NLU Core (LLM)**: Intent + slot extraction (action, device, location, value, time).
* **Entity Resolver**: Maps slots to concrete devices using ontology + embeddings + context.
* **Policy & Safety Guard**: Capability check, range limits, privacy/role rules.
* **Command Synthesizer**: Translates intent → device-specific payloads.
* **Dispatcher (MQTT)**: Publishes with QoS, correlation IDs, retries.
* **Telemetry & Feedback Monitor**: Correlates acks/status, closes loop with user.
* **Learning Loop**: Adds synonyms, corrections, and patterns to memory/ontology.

---

## 1) Inputs → Outputs (per request)

### Input

* `utterance`: “make the bedroom a bit cooler for 30 mins”
* `context`: userId, default\_room, preferred\_units, device history, scene/mode, time
* `device_catalog`: registry of devices, capabilities, topics, synonyms, embeddings
* `policy`: safety ranges, roles, critical actions, confirmation rules

### Output

* `executionPlan`: list of device actions (topic, payload, qos, retain)
* `clarifications` (optional): questions if ambiguity/risk detected
* `finalUserMessage`: confirmation or error with remediation
* `telemetry`: correlationId, timestamps, outcomes for observability

---

## 2) Step-by-Step Flow

1. **Ingest & Normalize**

   * Lowercase, strip punctuation, fix spelling (“bedrom”→“bedroom”).
   * Expand colloquialisms (“a bit cooler”→“decrease temperature”).

2. **LLM Intent & Slot Extraction**

   * Prompted with your home ontology schema.
   * Returns JSON:

     ```json
     {
       "intent":"adjust_temperature",
       "device_mentions":["bedroom ac", "thermostat"],
       "location":"bedroom",
       "delta":-2,
       "duration":"30m",
       "confidence":0.86
     }
     ```

3. **Slot Validation & Defaulting**

   * If both AC and thermostat possible, prefer room AC if present.
   * If absolute `targetTemperature` missing but delta present, compute from current state.
   * Convert units (°F/°C), parse time (“30m”→1800s).

4. **Entity Resolution (Core LLM Resolution Task)**

   * **String match** (normalized name/synonyms) → shortlist.
   * **Embedding match** between “bedroom ac” and device names/labels → similarity score.
   * **Context boost**: user’s last-controlled device in that room (+λ), device availability (online), capability presence.
   * **Tie-break** rules: strongest overall score; if < threshold or multiple within ε → ambiguity.
   * **Ambiguity protocol**: generate **focused clarification** (“I found two bedroom ACs: ‘Master Bedroom AC Ultra’ and ‘Guest Bedroom AC’. Which one?”). Include compact spec chips (online/offline, mode, temp).

5. **Capability & Policy Checks**

   * Verify device supports `temperature` and `timer`.
   * Clamp values to safe ranges (16–30°C). If out of bounds, propose nearest allowed value.
   * Sensitive actions (e.g., unlocking, arming) may require explicit confirmation.

6. **Confirmation Gate (Situational)**

   * If low confidence, high-risk, or high cost:
     “Set **Master Bedroom AC** to **21°C** for **30 min**, quiet mode on. Proceed?”
   * Otherwise, proceed silently and **speak-back** the plan post-execution.

7. **Command Synthesis**

   * Build device-specific payloads via adapter:

     ```json
     {
       "targetTemperature": 21,
       "mode": "cool",
       "timer": 1800,
       "quietMode": true
     }
     ```
   * Select MQTT topic from catalog: `home/bedroom/ac/set/temperature`, etc.
   * Attach `correlationId` and `timestamp`.

8. **Dispatch over MQTT**

   * Publish each action with QoS 1 or 2 (idempotent where possible).
   * Persist `pendingTransactions[correlationId]` with timeout & retry policy.

9. **Feedback Correlation**

   * Listen on `+/status` or device’s LWT/ack topic.
   * Match `correlationId`. If success: mark complete; if error: capture code (`E_CAPABILITY`, `E_OFFLINE`, `E_RANGE`).

10. **Autonomous Repair (LLM-driven)**

    * If `E_OFFLINE`: suggest alternative device in same zone (“bedroom thermostat zone control”) or ask to switch power.
    * If `E_RANGE`: re-clamp and retry once; otherwise ask user.
    * If `E_CAPABILITY`: propose nearest equivalent action (“fan speed to low, eco mode on”).

11. **User Closure**

    * Natural, concise result:
      “Done. **Master Bedroom AC** set to **21°C** for **30 min** (quiet). Current 22.7°C → trending to target.”

12. **Learning & Memory Update**

    * Add “MBR AC” → `ac_bedroom_001` synonym.
    * Add corrected phrases to few-shot examples.
    * Update device affinity for user/room.

---

## 3) Device Catalog / Ontology (Key Fields)

| Field          | Example                                                        | Notes              |
| -------------- | -------------------------------------------------------------- | ------------------ |
| `id`           | `ac_bedroom_001`                                               | Unique key         |
| `labels`       | `["bedroom ac","master ac","ultra-z5000"]`                     | Names/synonyms     |
| `room`         | `master bedroom`                                               | For context boost  |
| `capabilities` | `["power","temperature","mode","timer","quietMode"]`           | Drives suitability |
| `mqtt`         | `{status:"home/bedroom/ac/status", set:"home/bedroom/ac/set"}` | Topics             |
| `adapters`     | `mirAIe.ac.v3`                                                 | Payload translator |
| `embeddings`   | vector                                                         | For semantic match |
| `state`        | `{temp:22.8,target:23,mode:"cool"}`                            | Live snapshot      |

---

## 4) Ambiguity & Error Playbooks (LLM Prompts)

**Clarify Device (multiple matches):**
*“I found 2 ACs in ‘bedroom’. A) Master Bedroom AC (online, 22.8→23°C) B) Guest Bedroom AC (offline). Which one?”*

**Missing Slot:**
*“What temperature would you like for the bedroom AC? (16–30°C)”*

**Unsafe / Out of Range:**
*“27°C exceeds the ‘server closet’ cap (max 24°C). Apply 24°C instead?”*

**Unavailable Device:**
*“Bedroom AC is offline. I can set the zone thermostat to 23°C or turn on the Living Room AC to support cooling. Choose?”*

---

## 5) Algorithmic Skeleton (Pseudocode)

```python
def handle_request(utterance, context):
    text = normalize(utterance)
    nlu = llm_extract(text, schema=HOME_ONTOLOGY)

    slots = fill_defaults(nlu, context)
    candidates = shortlist_devices(slots, device_catalog)

    resolved = resolve_entity(
        mentions=slots.device_mentions,
        room=slots.location,
        candidates=candidates,
        embeddings=device_catalog.embeddings,
        history=context.history
    )

    if resolved.ambiguity > THRESHOLD:
        return ask_clarification(resolved.options)

    plan = build_plan(resolved.device, slots)
    violations = policy_check(plan, policy, device_catalog)

    if violations.require_confirmation:
        if not user_confirm(plan, violations): return abort()

    msgs = synthesize_payloads(plan, adapter=resolved.device.adapter)
    corr = dispatch_mqtt(msgs, qos=1)

    outcome = await_feedback(corr, timeout=FEEDBACK_TTL)
    if not outcome.success:
        repaired = try_repair(outcome, plan, device_catalog, context)
        if repaired:
            return finalize(repaired)
        else:
            return report_failure(outcome)

    learn_synonyms(nlu, resolved)
    return finalize(outcome)
```

---

## 6) MQTT Contract (Operational)

| Aspect      | Spec                                                 |
| ----------- | ---------------------------------------------------- |
| QoS         | 1 for idempotent set; 2 for safety-critical          |
| Topics      | `home/{room}/{device}/set/{action}` and `.../status` |
| Payload     | JSON with `action`, `params`, `correlationId`, `ts`  |
| Correlation | UUIDv4 tied to pending transactions                  |
| Retries     | Exponential backoff (e.g., 0.5s/1s/2s up to N)       |
| Timeouts    | Device class–specific (AC: 5s status ack)            |
| LWT         | Marks device offline → resolver will avoid it        |

---

## 7) Edge Cases & How Agent Handles Them

* **Vague phrasing**: “Make it comfy” → map to `comfort_profile` per user, derive temperature + fan + quiet.
* **Conflicting commands**: Two requests overlap; orchestrator deduplicates by device and merges (last write wins or policy).
* **Chain intents**: “Dim lights and cool bedroom to 22” → multi-action plan → parallel dispatch with per-device correlation.
* **Room inference**: No room specified; use user’s presence (BLE/Wi-Fi), last active room, or default profile.
* **Device firmware variance**: Adapter negotiates payload keys; falls back to minimal set if capability missing.

---

## 8) Quality & Safety Gates (What to Track)

| KPI                                     | Target                               |
| --------------------------------------- | ------------------------------------ |
| Intent accuracy                         | > 95% (offline eval)                 |
| First-try resolution (no clarification) | > 80%                                |
| Mean clarification count                | < 0.3 per task                       |
| End-to-end P95 latency                  | < 1.2s (local LLM) / < 2.5s (remote) |
| Command success rate                    | > 99% (with retries)                 |
| False-actuation incidents               | 0 (policy + confirmations)           |

---

## 9) Minimal State Machine (text)

```
IDLE
  -> (utterance) → PARSE
PARSE
  -> (high_conf && slots_complete) → RESOLVE
  -> (low_conf || missing_slots) → CLARIFY
CLARIFY
  -> (user_answer) → PARSE (with constraints)
RESOLVE
  -> (ambiguous) → CLARIFY
  -> (resolved) → POLICY_CHECK
POLICY_CHECK
  -> (violation && needs_confirm) → CONFIRM
  -> (ok) → SYNTHESIZE
CONFIRM
  -> (accept) → SYNTHESIZE
  -> (decline) → ABORT
SYNTHESIZE
  -> DISPATCH
DISPATCH
  -> (ack) → MONITOR
  -> (no_ack/err) → REPAIR
REPAIR
  -> (recovered) → MONITOR
  -> (fail) → REPORT
MONITOR
  -> (success) → CLOSE
REPORT/CLOSE
  -> IDLE
```

---

## 10) Example: From Messy Input to Action

**User**: “hey cool my master bed ac a little, keep it quiet for half an hour”
**Agent resolution**:

1. Normalize → “cool master bedroom ac a little, quiet, 30 minutes”.
2. LLM: `intent=adjust_temperature`, `delta=-2`, `duration=1800s`, `modes=["quiet"]`.
3. Resolve “master bedroom ac” → `ac_bedroom_001` (online, supports quiet/timer).
4. Compute target: current 23 → 21°C (clamp if necessary).
5. Policy: OK; needs no explicit confirm (non-critical).
6. Synthesize payload(s):

   * `home/bedroom/ac/set` → `{"targetTemperature":21,"quietMode":true,"timer":1800,"correlationId":"..."}`
7. Dispatch QoS1; await status:

   * Ack: `{"power":true,"temp":22.7,"target":21,"quietMode":true,"timer":1800,"correlationId":"..."}`
8. Close loop: “Set to 21°C, quiet for 30m. Now 22.7°C and dropping.”

---


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

