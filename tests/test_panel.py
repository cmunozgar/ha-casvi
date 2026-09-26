"""School panel, access control, and durable notification behavior."""
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from homeassistant.exceptions import HomeAssistantError, Unauthorized
from custom_components.casvi.notifications import MessageNotifications
from custom_components.casvi.panel import ws_overview, ws_message
from custom_components.casvi.api import CasviClient


def row(id='1', date='2026-09-26 12:00:00', recipient=2):
    return {'id': id, 'idPara': recipient, 'fechaEnvio': date}


def notifier(saved=None):
    hass = MagicMock()
    hass.services.async_call = AsyncMock()
    entry = SimpleNamespace(entry_id='account', options={'notify_targets': ['mobile_app_test']})
    with patch('custom_components.casvi.notifications.Store') as store:
        store.return_value.async_load = AsyncMock(return_value=deepcopy(saved))
        store.return_value.async_save = AsyncMock()
        tracker = MessageNotifications(hass, entry)
    return tracker, hass


@pytest.mark.asyncio
async def test_initial_inbox_never_notifies_and_repeat_is_silent():
    tracker, hass = notifier()
    await tracker.process([row()])
    await tracker.process([row()])
    hass.services.async_call.assert_not_awaited()
    assert tracker.state['seen']


@pytest.mark.asyncio
async def test_new_message_notifies_once_after_restart_without_private_content():
    tracker, hass = notifier()
    await tracker.process([row()])
    tracker, hass = notifier(tracker.state)
    new = row('2', '2026-09-27 12:00:00')
    await tracker.process([new, row()])
    await tracker.process([new, row()])
    hass.services.async_call.assert_awaited_once()
    payload = hass.services.async_call.call_args.args[2]
    assert payload['message'] == 'Tienes un nuevo mensaje. Toca para leerlo.'
    assert 'entry=account' in payload['data']['url']
    assert 'message=2' in payload['data']['url']
    assert payload['data']['url'] == payload['data']['clickAction']
    assert not tracker.state['pending']


@pytest.mark.asyncio
async def test_same_message_different_recipient_and_history_expansion():
    tracker, hass = notifier()
    await tracker.process([row()])
    await tracker.process([row('0', '2026-09-20 12:00:00')])
    hass.services.async_call.assert_not_awaited()
    await tracker.process([row('2', '2026-09-27 12:00:00', 3), row('2', '2026-09-27 12:00:00', 4)])
    assert hass.services.async_call.await_count == 2


@pytest.mark.asyncio
async def test_failed_delivery_is_persisted_and_retried_after_restart():
    tracker, hass = notifier()
    await tracker.process([row()])
    hass.services.async_call.side_effect = HomeAssistantError()
    await tracker.process([row('2', '2026-09-27 12:00:00')])
    assert tracker.state['pending']
    tracker, hass = notifier(tracker.state)
    await tracker.process([])
    hass.services.async_call.assert_awaited_once()
    assert not tracker.state['pending']


@pytest.mark.asyncio
async def test_delivery_retries_bounded_and_disabled_targets_are_removed():
    tracker, hass = notifier()
    await tracker.process([row()])
    hass.services.async_call.side_effect = HomeAssistantError()
    for _ in range(4):
        await tracker.process([row('2', '2026-09-27 12:00:00')])
    assert hass.services.async_call.await_count == 3
    assert not tracker.state['pending']
    await tracker.process([row('3', '2026-09-28 12:00:00')])
    tracker.entry.options['notify_targets'] = []
    await tracker.process([])
    assert not tracker.state['pending']


def test_panel_commands_reject_non_admins():
    connection = MagicMock()
    connection.user.is_admin = False
    for command in (ws_overview, ws_message):
        with pytest.raises(Unauthorized):
            command(MagicMock(), connection, {'id': 1})
    connection.send_result.assert_not_called()


@pytest.mark.asyncio
async def test_message_only_fetches_explicitly_selected_inbox_pair():
    coordinator = SimpleNamespace(data={'messages': [row()]}, client=SimpleNamespace(read_message=AsyncMock(return_value={'mensaje':'<p>Hello</p>'})), async_request_refresh=AsyncMock())
    hass = SimpleNamespace(data={'casvi': {'account': coordinator}})
    connection = MagicMock()
    # Exercise async handler below the framework auth/scheduling wrappers.
    handler = ws_message.__wrapped__.__wrapped__
    await handler(hass, connection, {'id': 1, 'entry_id': 'account', 'message_id':'1', 'recipient_id':'999'})
    coordinator.client.read_message.assert_not_awaited()
    connection.send_error.assert_called_once()
    await handler(hass, connection, {'id': 2, 'entry_id': 'account', 'message_id':'1', 'recipient_id':'2'})
    coordinator.client.read_message.assert_awaited_once_with('1', 2)
    assert connection.send_result.call_args.args[1]['content'] == 'Hello'


@pytest.mark.asyncio
async def test_explicit_read_uses_detail_action_without_mark_read():
    client = CasviClient('test', 'test')
    client._login = AsyncMock()
    client._check = AsyncMock()
    client._request = AsyncMock(return_value={'success': True, 'data': {'mensaje': 'Hello'}})
    assert (await client.read_message('1','2'))['mensaje'] == 'Hello'
    client._request.assert_awaited_once_with('/controles/mensajesAdmin.php', {'accion':'ver_mensaje_recibido','id_mensaje':'1','id_para':'2'})
