import asyncio
from contextlib import asynccontextmanager


class KeyLock:
    def __init__(self):
        self._locks: dict[str, asyncio.Lock] = {}

    @asynccontextmanager
    async def __call__(self, id):
        lock = self._locks.setdefault(id, asyncio.Lock())
        async with lock:
            yield
