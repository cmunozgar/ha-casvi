"""Account-local school-year cache shared by the panel and schedule reader."""
import asyncio
from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from homeassistant.helpers.storage import Store


class ProfileCache:
    def __init__(self, hass, client, entry_id):
        self.client = client
        self.store = Store(hass, 1, f'casvi.profiles.{entry_id}')
        self.cache = None
        self.lock = asyncio.Lock()

    async def read(self, child, today=None):
        today = today or datetime.now(ZoneInfo('Europe/Madrid')).date()
        year = today.year if today.month >= 9 else today.year - 1
        async with self.lock:
            if self.cache is None:
                self.cache = await self.store.async_load() or {}
            cached = self.cache.get(child)
            if cached and cached['year'] == year:
                return deepcopy(cached['profile'])
            profile = await self.client.child_profile(child)
            # Do not freeze an incomplete response for an entire school year.
            if profile.get('group') and profile.get('teachers_available', True):
                self.cache[child] = {'year': year, 'profile': deepcopy(profile)}
                await self.store.async_save(self.cache)
            return profile

    async def invalidate(self):
        async with self.lock:
            self.cache = {}
            await self.store.async_save(self.cache)
