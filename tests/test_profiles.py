from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import asyncio
import pytest
from custom_components.casvi.profiles import ProfileCache


@pytest.mark.asyncio
async def test_persistent_cache_school_year_and_manual_refresh():
    profile = {'group': {'idGrupo': '1'}, 'teachers': [{'name': 'Teacher'}], 'classmates': ['Student'], 'teachers_available': True}
    client = SimpleNamespace(child_profile=AsyncMock(return_value=profile))
    with patch('custom_components.casvi.profiles.Store') as factory:
        store = factory.return_value
        store.async_load = AsyncMock(return_value=None)
        store.async_save = AsyncMock()
        cache = ProfileCache(None, client, 'account')
        results = await asyncio.gather(*(cache.read('child', date(2026, 9, 1)) for _ in range(3)))
        client.child_profile.assert_awaited_once()
        results[0]['teachers'].clear()
        assert (await cache.read('child', date(2027, 8, 31)))['teachers']
        store.async_load.return_value = cache.cache
        restarted = ProfileCache(None, client, 'account')
        await restarted.read('child', date(2027, 8, 31))
        assert client.child_profile.await_count == 1
        await restarted.read('child', date(2027, 9, 1))
        assert client.child_profile.await_count == 2
        await restarted.invalidate()
        await restarted.read('child', date(2027, 9, 1))
        assert client.child_profile.await_count == 3


@pytest.mark.asyncio
async def test_incomplete_profiles_are_retried_and_children_are_separate():
    client = SimpleNamespace(child_profile=AsyncMock(return_value={'group': {'idGrupo': '1'}, 'teachers_available': False}))
    with patch('custom_components.casvi.profiles.Store') as factory:
        factory.return_value.async_load = AsyncMock(return_value={})
        factory.return_value.async_save = AsyncMock()
        cache = ProfileCache(None, client, 'account')
        await cache.read('one')
        await cache.read('one')
        assert client.child_profile.await_count == 2
        factory.return_value.async_save.assert_not_awaited()
        client.child_profile.return_value = {'group': {'idGrupo': '1'}, 'teachers_available': True}
        await cache.read('one')
        await cache.read('two')
        assert set(cache.cache) == {'one', 'two'}
