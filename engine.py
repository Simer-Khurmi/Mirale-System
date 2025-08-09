import os, re, json, asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from langdetect import detect

PROVIDER = os.getenv("LLM_PROVIDER", "rule").lower()
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "en").lower()

class ParsedCommand(BaseModel):
    intent: str
    action: str
    device: Optional[str] = None
    room: Optional[str] = None
    params: Dict[str, Any] = {}
    confidence: float = 0.65
    ambiguities: List[str] = []

# Simple bilingual lexicon (en/fr) for core actions/entities
LEXICON = {
    "turn_on": ["turn on", "switch on", "power on", "allumer"],
    "turn_off": ["turn off", "switch off", "power off", "éteindre", "eteindre"],
    "set_temp": ["set temperature", "set temp", "temp to", "régler", "mettre à"],
    "swing": ["swing", "oscillation", "balayage"],
    "mode": ["mode", "cool", "heat", "fan", "dry", "chauffage", "froid"],
    "open": ["open", "ouvrir"],
    "close": ["close", "fermer"],
    "scene": ["scene", "scène", "movie", "reading", "party", "sleep", "work"],
    "energy": ["energy", "consumption", "usage", "énergie", "consommation"]
}

ROOMS = ["living room", "bedroom", "master bedroom", "office", "home office", "kitchen", "hallway", "salon", "chambre", "bureau", "cuisine"]

class LLMEngine:
    def __init__(self):
        pass

    async def parse(self, text: str, lang_hint: Optional[str] = None) -> ParsedCommand:
        lang = (lang_hint or self._detect_lang(text) or DEFAULT_LANG)
        # First do deterministic parse with fallbacks
        parsed = self._rule_parse(text, lang)
        if PROVIDER == "openai":
            try:
                enriched = await self._openai_enrich(text, parsed, lang)
                return enriched
            except Exception:
                # Fall back gracefully
                parsed.ambiguities.append("LLM provider failed; used rule-based parse.")
        return parsed

    def _detect_lang(self, text: str) -> str:
        try:
            return detect(text)
        except Exception:
            return DEFAULT_LANG

    def _rule_parse(self, text: str, lang: str) -> ParsedCommand:
        t = text.lower().strip()

        # Extract room if present
        room = None
        for r in ROOMS:
            if r in t:
                room = r
                break

        # Determine device type heuristically
        device = None
        if any(w in t for w in ["ac", "air condition", "climatiseur"]):
            device = "air_conditioner"
        elif any(w in t for w in ["light", "lamp", "lumière", "lumiere"]):
            device = "light"
        elif any(w in t for w in ["curtain", "blind", "rideau"]):
            device = "curtain"
        elif any(w in t for w in ["fan", "ventilateur"]):
            device = "fan"
        elif any(w in t for w in ["security", "alarm", "sécurité", "securite"]):
            device = "security"

        # Actions
        def match_any(keys: List[str]) -> bool:
            return any(any(k in t for k in LEXICON[key]) for key in keys)

        if match_any(["turn_on"]) and device:
            return ParsedCommand(intent="device_control", action="power_on", device=device, room=room, confidence=0.85)
        if match_any(["turn_off"]) and device:
            return ParsedCommand(intent="device_control", action="power_off", device=device, room=room, confidence=0.85)

        # Temperature
        m = re.search(r"(?:to|à|a)\s*(\d{1,2})", t)
        if device in ("air_conditioner", "thermostat") and m:
            temp = int(m.group(1))
            return ParsedCommand(intent="climate", action="set_temperature", device=device, room=room, params={"target": temp}, confidence=0.8)

        # Swing timer
        if "swing" in t or "oscillation" in t or "balayage" in t:
            tm = re.search(r"(\d+)\s*(min|minute|minutes|hr|hour|heures?)", t)
            seconds = None
            if tm:
                val = int(tm.group(1))
                unit = tm.group(2)
                seconds = val * 3600 if unit.startswith(("hr","hour","heur")) else val * 60
            return ParsedCommand(intent="climate", action="set_swing", device=device or "air_conditioner", room=room, params={"timer": seconds or 1800}, confidence=0.75)

        # Scenes
        if "scene" in t or "scène" in t or any(s in t for s in ["movie","reading","party","sleep","work"]):
            sc = None
            for s in ["movie","reading","party","sleep","work"]:
                if s in t:
                    sc = s
                    break
            return ParsedCommand(intent="lighting", action="set_scene", device="light", room=room, params={"scene": sc or "movie"}, confidence=0.7)

        # Energy
        if any(w in t for w in LEXICON["energy"]):
            return ParsedCommand(intent="reporting", action="energy_report", params={}, confidence=0.8)

        # Open/Close curtains
        if device == "curtain":
            if match_any(["open"]):
                return ParsedCommand(intent="curtain", action="open", device="curtain", room=room, confidence=0.8)
            if match_any(["close"]):
                return ParsedCommand(intent="curtain", action="close", device="curtain", room=room, confidence=0.8)

        # Fallback
        return ParsedCommand(intent="unknown", action="unknown", ambiguities=["Could not infer device/action. Please clarify room/device."], confidence=0.4)

    async def _openai_enrich(self, text: str, parsed: ParsedCommand, lang: str) -> ParsedCommand:
        # Optional enrichment (kept minimal to avoid hard dependency at runtime without key)
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return parsed
        client = OpenAI(api_key=api_key)
        sys = "You convert home-automation requests into a strict JSON schema: {intent, action, device?, room?, params{}, confidence(0-1), ambiguities[]}"
        msg = [
            {"role":"system","content":sys},
            {"role":"user","content":f"Request (lang={lang}): {text}. Prior parse: {parsed.model_dump()}. Return ONLY valid JSON."}
        ]
        res = await asyncio.to_thread(client.chat.completions.create, model="gpt-4o-mini", messages=msg, temperature=0.2)
        raw = res.choices[0].message.content.strip()
        try:
            data = json.loads(raw)
            return ParsedCommand(**data)
        except Exception:
            parsed.ambiguities.append("LLM JSON parse failed; using rule parse.")
            return parsed
