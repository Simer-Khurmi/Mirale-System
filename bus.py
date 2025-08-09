import asyncio
from typing import Callable, Any, List, Deque, Dict
from collections import deque
from pydantic import BaseModel

class Event(BaseModel):
    type: str
    payload: Dict

class EventBus:
    def __init__(self, maxlen: int = 1000):
        self._subs: List[Callable[[Any], Any]] = []
        self._queue: asyncio.Queue = asyncio.Queue()
        self._log: Deque[Dict] = deque(maxlen=maxlen)
        self._task = asyncio.create_task(self._pump())

    def tail(self, limit: int = 200):
        return list(self._log)[-limit:]

    def subscribe(self, fn):
        self._subs.append(fn)
        return fn

    async def emit(self, evt: Event):
        self._log.append(evt.model_dump())
        await self._queue.put(evt)

    async def _pump(self):
        while True:
            evt: Event = await self._queue.get()
            for fn in list(self._subs):
                res = fn(evt)
                if asyncio.iscoroutine(res):
                    await res
