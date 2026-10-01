from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from custom_components.casvi.event_tracking import EventTracker
from custom_components.casvi.sensor import CasviNewEvents, CasviUnreadWidget
from custom_components.casvi.binary_sensor import CasviActivity


@pytest.mark.asyncio
async def test_initial_history_duplicates_restart_and_reappearing_events():
    tracker = EventTracker.__new__(EventTracker)
    tracker.store = SimpleNamespace(async_load=AsyncMock(return_value=None), async_save=AsyncMock())
    tracker.state = None
    tracker.entry = None
    assert await tracker.process({'a': [{'id': 1}, {'id': 1}]}) == {'a': 0}
    assert await tracker.process({'a': [{'id': 1}, {'id': 2}], 'b': [{'id': 2}]}) == {'a': 1, 'b': 0}
    saved = deepcopy(tracker.state)
    tracker.state = None
    tracker.entry = None
    tracker.store.async_load.return_value = saved
    assert await tracker.process({'a': [], 'b': []}) == {'a': 1, 'b': 0}
    assert await tracker.process({'a': [{'id': 1}, {'id': 2}, {'id': 3}], 'b': [{'id': 2}, {'id': 3}]}) == {'a': 2, 'b': 1}


def test_names_and_event_count():
    c = SimpleNamespace(entry=SimpleNamespace(entry_id='account'), children={'a': 'Lucas Apellido Apellido'}, last_update_success=True, data={'new_events': {'a': 2, 'b': 3}})
    assert CasviNewEvents(c).native_value == 5
    assert CasviNewEvents(c, 'a').native_value == 2
    assert CasviUnreadWidget(c, child='a').name == 'Casvi Lucas Mensaje no leído 1'
    assert CasviActivity(c, 'a', c.children['a'], 'pool').name == 'Casvi Lucas Piscina hoy'
    assert CasviActivity(c, 'a', c.children['a'], 'pool').unique_id == 'account_a_pool_today'


@pytest.mark.asyncio
async def test_event_notifications_opt_in_and_no_initial_history():
    tracker = EventTracker.__new__(EventTracker)
    tracker.store = SimpleNamespace(async_load=AsyncMock(return_value=None), async_save=AsyncMock())
    tracker.hass = SimpleNamespace(services=SimpleNamespace(async_call=AsyncMock()))
    tracker.entry = SimpleNamespace(options={'notify_targets': ['mobile_app_phone'], 'notify_events': False}, data={'children': {'a': 'Lucas Apellido'}})
    tracker.state = None
    await tracker.process({'a': [{'id': 1}]})
    await tracker.process({'a': [{'id': 1}, {'id': 2}]})
    tracker.hass.services.async_call.assert_not_called()
    tracker.entry.options['notify_events'] = True
    await tracker.process({'a': [{'id': 1}, {'id': 2}]})
    tracker.hass.services.async_call.assert_not_called()
    rows = [{'id': 1}, {'id': 2}, {'id': 3, 'title': 'Excursión', 'start': '2026-10-02T09:00:00'}]
    await tracker.process({'a': rows})
    tracker.hass.services.async_call.assert_called_once()
    assert 'Lucas · Excursión' in tracker.hass.services.async_call.call_args.args[2]['message']
    await tracker.process({'a': rows})
    tracker.hass.services.async_call.assert_called_once()
