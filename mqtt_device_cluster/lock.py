import asyncio
from contextlib import asynccontextmanager


class KeyLock:
    def __init__(self):
        self._locks: dict[str, asyncio.Lock] = {}

    @asynccontextmanager
    async def __call__(self, id):
        if not self._locks.get(id):
            self._locks[id] = asyncio.Lock()
        async with self._locks[id]:
            yield
        del self._locks[id]
