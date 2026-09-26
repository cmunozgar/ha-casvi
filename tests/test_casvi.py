"""Synthetic fixtures only; no school data or network credentials."""
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from zoneinfo import ZoneInfo
import pytest

from custom_components.casvi.api import (
    CasviClient, CasviAuthError, CasviError, SessionExpired, discover_children, plain_text,
)
from custom_components.casvi.calendar import calendar_events, CasviCalendar
from custom_components.casvi.config_flow import CasviConfigFlow
from custom_components.casvi.sensor import CasviSensor


@pytest.mark.asyncio
async def test_login_fields_and_session_validation():
    client = CasviClient('family', 'secret')
    client._request = AsyncMock(side_effect=['html', {'status': 'success'}, {'status': 'ok'}])
    await client._login()
    args = client._request.call_args_list[1]
    assert args.args[0] == '/controles/usuarios.php'
    assert args.args[1] == {'accion': 'login', 'usuario': 'family', 'pass': 'secret'}
    assert args.kwargs['multipart'] is True


@pytest.mark.asyncio
async def test_rejected_login_stops():
    client = CasviClient('family', 'secret')
    client._request = AsyncMock(side_effect=['html', {'status': 'error'}])
    with pytest.raises(CasviAuthError):
        await client._login()
    assert client._request.call_count == 2


@pytest.mark.asyncio
async def test_expired_session_reauthenticates_once():
    client = CasviClient('family', 'secret')
    client._session = MagicMock(close=AsyncMock())
    client._check = AsyncMock(side_effect=[SessionExpired(), None])
    client._login = AsyncMock()
    operation = AsyncMock(return_value={'value': 1})
    assert await client._authenticated(operation) == {'value': 1}
    client._login.assert_awaited_once()
    operation.assert_awaited_once()


@pytest.mark.asyncio
async def test_silent_empty_response_discarded_if_session_expired_mid_poll():
    client = CasviClient('family', 'secret')
    client._login = AsyncMock()
    client._check = AsyncMock(side_effect=[SessionExpired(), None])
    operation = AsyncMock(side_effect=[[], ['actual data']])
    assert await client._authenticated(operation) == ['actual data']
    assert operation.await_count == 2


@pytest.mark.asyncio
async def test_retry_is_bounded():
    client = CasviClient('family', 'secret')
    client._login = AsyncMock()
    client._check = AsyncMock(side_effect=SessionExpired())
    with pytest.raises(CasviAuthError):
        await client._authenticated(AsyncMock(return_value=[]))
    assert client._login.await_count == 2


@pytest.mark.asyncio
async def test_network_failure_does_not_trigger_password_retry():
    client = CasviClient('family', 'secret')
    client._login = AsyncMock(side_effect=CasviError('offline'))
    with pytest.raises(CasviError):
        await client._authenticated(AsyncMock())
    client._login.assert_awaited_once()


@pytest.mark.asyncio
async def test_unread_message_body_not_fetched():
    client = CasviClient('family', 'secret')
    client._login = AsyncMock()
    client._check = AsyncMock()
    client._request = AsyncMock(side_effect=[
        {'success': True, 'total': '100', 'data': [{'id': '1', 'idPara': 2, 'leido': '0'}]},
        {'error': 0, 'menus': []}, {'status': 'success', 'data': []},
    ])
    result = await client.snapshot({'123': 'Child'}, date(2026, 9, 1))
    assert result['detail'] is None
    actions = [call.args[1]['accion'] for call in client._request.call_args_list]
    assert actions == ['listar_mensajes_recibidos', 'obtener_menus_mes', 'get_eventos_alumno_especifico']
    assert result['total'] == 100


@pytest.mark.asyncio
async def test_read_message_body_uses_both_identifiers():
    client = CasviClient('family', 'secret')
    client._login = AsyncMock()
    client._check = AsyncMock()
    client._request = AsyncMock(side_effect=[
        {'success': True, 'total': '1', 'data': [{'id': '1', 'idPara': 2, 'leido': '1'}]},
        {'error': 0, 'menus': []}, {'success': True, 'data': {'mensaje': '<p>Hello</p>'}},
    ])
    result = await client.snapshot({}, date(2026, 9, 1))
    assert result['detail']['mensaje'] == '<p>Hello</p>'
    assert client._request.call_args.args[1] == {'accion': 'ver_mensaje_recibido', 'id_mensaje': '1', 'id_para': '2'}


def test_children_only_from_family_navigation():
    html = '<a href="#hijoMenu-123"><span class="area-padre-hijo-nombre">Child &amp; family</span></a><a href="agenda.php?idUsuAlumno=123">Agenda</a><a href="other.php?idUsuAlumno=456">Other</a>'
    assert discover_children(html) == {'123': 'Child & family'}


def test_html_is_converted_without_script_content():
    assert plain_text('<p>Hello</p><script>secret()</script><p>World &amp; us</p>') == 'Hello\n\nWorld & us'
    assert plain_text('one\\r\\ntwo') == 'one\ntwo'


def test_calendar_time_zone_and_recurring_instances():
    rows = [{'id': '1', 'start': '2026-09-26T09:30:00.0000000', 'title': 'Event'},
            {'id': '1', 'start': '2026-09-27T09:30:00', 'title': 'Event'},
            {'id': '1', 'start': '2026-09-27T09:30:00', 'title': 'Duplicate'},
            {'start': 'bad'}]
    events = calendar_events(rows)
    assert len(events) == 2
    assert events[0].start.utcoffset() == timedelta(hours=2)
    assert events[0].end - events[0].start == timedelta(minutes=1)


@pytest.mark.asyncio
async def test_calendar_interval_boundaries():
    coordinator = MagicMock()
    coordinator.entry.entry_id = 'test'
    coordinator.data = {'agenda': {'1': [{'id': 'e', 'start': '2026-09-26T10:00:00', 'title': 'Event'}]}}
    calendar = CasviCalendar(coordinator, '1', 'Child')
    start = datetime(2026, 9, 26, 10, tzinfo=ZoneInfo('Europe/Madrid'))
    assert len(await calendar.async_get_events(None, start, start + timedelta(hours=1))) == 1
    assert await calendar.async_get_events(None, start + timedelta(minutes=1), start + timedelta(hours=1)) == []


def test_sensor_state_bounded_and_unread_count_labelled():
    coordinator = MagicMock()
    coordinator.entry.entry_id = 'test'
    coordinator.data = {'messages': [{'asunto': 'a' * 400, 'leido': '0'}], 'total': 1000}
    sensor = CasviSensor(coordinator, 'latest', 'Latest')
    assert len(sensor.native_value) == 250
    unread = CasviSensor(coordinator, 'unread', 'Unread recent')
    assert unread.native_value == 1
    assert unread.extra_state_attributes['mensajes_examinados'] == 1


def test_config_flow_can_load():
    assert CasviConfigFlow.VERSION == 1


@pytest.mark.asyncio
async def test_login_page_allowed_only_at_public_root():
    client = CasviClient('family', 'secret')
    response = MagicMock(status=200)
    response.text = AsyncMock(return_value='<form id="login_form"></form>')
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=response)
    context.__aexit__ = AsyncMock(return_value=False)
    client._session = MagicMock()
    client._session.request.return_value = context
    assert 'login_form' in await client._request('/', text=True)
    with pytest.raises(SessionExpired):
        await client._request('/pages/escritorio.php', text=True)
