"""School panel, access control, and durable notification behavior."""
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from homeassistant.exceptions import HomeAssistantError, Unauthorized
from custom_components.casvi.notifications import MessageNotifications
from custom_components.casvi.panel import ws_overview, ws_message, ws_messages, ws_child, ws_document
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
    for command in (ws_overview, ws_message, ws_messages, ws_child, ws_document):
        with pytest.raises(Unauthorized):
            command(MagicMock(), connection, {'id': 1})
    connection.send_result.assert_not_called()


@pytest.mark.asyncio
async def test_message_only_fetches_explicitly_selected_inbox_pair():
    coordinator = SimpleNamespace(children={}, data={'messages': [row()]}, client=SimpleNamespace(mark_message_read=AsyncMock(),read_message=AsyncMock(return_value={'mensaje':'<p>Hello</p>'})), async_request_refresh=AsyncMock())
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
    coordinator.client.mark_message_read.assert_awaited_once_with('1', 2)
    assert connection.send_result.call_args.args[1]['read'] is True


@pytest.mark.asyncio
async def test_explicit_read_uses_detail_action_without_mark_read():
    client = CasviClient('test', 'test')
    client._login = AsyncMock()
    client._check = AsyncMock()
    client._request = AsyncMock(return_value={'success': True, 'data': {'mensaje': 'Hello'}})
    assert (await client.read_message('1','2'))['mensaje'] == 'Hello'
    client._request.assert_awaited_once_with('/controles/mensajesAdmin.php', {'accion':'ver_mensaje_recibido','id_mensaje':'1','id_para':'2'})


def test_message_recipients_multiple_and_missing_are_not_guessed():
    from custom_components.casvi.panel import message_summary
    value = row()
    value['alumnosReferidos'] = [{'id': 'a', 'nombre_completo':'Child A'}, {'id':'b','nombre_completo':'Child B'}]
    assert len(message_summary(value, {})['children']) == 2
    assert message_summary(row(), {'a':'Child A'})['children'] == []
    fallback = row();fallback['idUsuAlumno'] = 'a'
    assert message_summary(fallback, {'a':'Child A'})['children'][0]['name'] == 'Child A'


def test_profile_respects_parent_visibility_and_omits_unneeded_fields():
    from custom_components.casvi.panel import profile_summary
    profile = profile_summary({'group':{'idGrupo':1,'documentos':[{'id':1,'titulo':'Horario'}]},
        'classmates':[{'nombre':'Example','apellido1':'Not exposed'}],
        'documents':[{'id':2,'titulo':'Visible','visiblePadre':1},{'id':3,'titulo':'Hidden','visiblePadre':0}],
        'tutorials':[{'motivo':'Meeting','visiblePadre':0,'resumen':'Private','planAccion':'Private'},
                     {'motivo':'Meeting','visiblePadre':1,'resumen':'Parent summary'}]})
    assert len(profile['documents']) == 2
    assert profile['classmates'] == ['Example']
    assert profile['tutorials'][0]['summary'] == ''
    assert profile['tutorials'][1]['summary'] == 'Parent summary'


@pytest.mark.asyncio
async def test_paginated_messages_authorize_historical_read_without_polling():
    from custom_components.casvi.panel import ws_messages
    client = SimpleNamespace(list_messages=AsyncMock(return_value={'messages':[row('old')],'total':101}),
        mark_message_read=AsyncMock(),read_message=AsyncMock(return_value={'mensaje':'Old content'}))
    c = SimpleNamespace(children={},data={'messages':[]},client=client,async_request_refresh=AsyncMock())
    hass = SimpleNamespace(data={'casvi':{'account':c}}); connection=MagicMock()
    await ws_messages.__wrapped__.__wrapped__(hass,connection,{'id':1,'entry_id':'account','start':100,'length':20})
    client.list_messages.assert_awaited_once_with(100,20)
    assert connection.send_result.call_args.args[1]['total'] == 101
    await ws_message.__wrapped__.__wrapped__(hass,connection,{'id':2,'entry_id':'account','message_id':'old','recipient_id':'2'})
    client.read_message.assert_awaited_once_with('old',2)


@pytest.mark.asyncio
async def test_child_and_document_reject_unselected_or_unknown_identifiers():
    from custom_components.casvi.panel import ws_child,ws_document
    client=SimpleNamespace(child_profile=AsyncMock(),read_document=AsyncMock())
    c=SimpleNamespace(children={'a':'Child'},client=client,panel_profiles={'a':{'documents':[]}})
    hass=SimpleNamespace(data={'casvi':{'account':c}});connection=MagicMock()
    await ws_child.__wrapped__.__wrapped__(hass,connection,{'id':1,'entry_id':'account','child_id':'other'})
    await ws_document.__wrapped__.__wrapped__(hass,connection,{'id':2,'entry_id':'account','child_id':'a','document_id':'unknown','kind':'documentoGrupo'})
    client.child_profile.assert_not_awaited();client.read_document.assert_not_awaited()


@pytest.mark.asyncio
async def test_list_messages_uses_server_pagination_and_validates_bounds():
    from custom_components.casvi.api import CasviError
    client=CasviClient('test','test');client._login=AsyncMock();client._check=AsyncMock()
    client._request=AsyncMock(return_value={'success':True,'data':[row()],'total':'101'})
    page=await client.list_messages(20,20)
    assert page['total']==101
    assert client._request.call_args.args[1]['start']=='20'
    with pytest.raises(CasviError):await client.list_messages(-1,20)
    with pytest.raises(CasviError):await client.list_messages(0,1000)


@pytest.mark.asyncio
async def test_pdf_download_uses_known_path_and_rejects_non_pdf():
    from custom_components.casvi.api import CasviError
    client=CasviClient('test','test');client._check=AsyncMock()
    async def chunks(size):
        yield b'not a PDF'
    response=MagicMock(status=200);response.content.iter_chunked=chunks
    context=MagicMock();context.__aenter__=AsyncMock(return_value=response);context.__aexit__=AsyncMock(return_value=False)
    client._session=MagicMock();client._session.get.return_value=context
    with pytest.raises(CasviError):await client.read_document('a',{'kind':'documentoGrupo','id':'doc','group':'group'})
    assert client._session.get.call_args.args[0].startswith('https://intranet.casvi.es/pages/verDocumento.php?')


@pytest.mark.asyncio
@pytest.mark.parametrize('payload,valid', [(b'%PDF-1.7\nexample',True), (b'%PDF-'+b'x'*(5*1024*1024),False)])
async def test_pdf_download_validates_magic_and_size(payload,valid):
    from custom_components.casvi.api import CasviError
    client=CasviClient('test','test');client._check=AsyncMock()
    async def chunks(size):
        yield payload
    response=MagicMock(status=200);response.content.iter_chunked=chunks
    context=MagicMock();context.__aenter__=AsyncMock(return_value=response);context.__aexit__=AsyncMock(return_value=False)
    client._session=MagicMock();client._session.get.return_value=context
    if valid:
        assert await client.read_document('a',{'kind':'documentoAlumno','id':'doc'})==payload
    else:
        with pytest.raises(CasviError):await client.read_document('a',{'kind':'documentoAlumno','id':'doc'})


def test_teachers_group_subjects_and_keep_photo_sources_server_side():
    from custom_components.casvi.panel import teachers_summary,public_profile
    teachers=teachers_summary([
        {'idProfesor':7,'profesor':'Example teacher','asignatura':'Math','foto':'https://example.invalid/photo'},
        {'idProfesor':7,'profesor':'Example teacher','asignatura':'Science'},
        {'idProfesor':7,'profesor':'Example teacher','asignatura':'Math'},
        {'profesor':'Other teacher','asignatura':'Music'},
    ])
    assert len(teachers)==2
    assert teachers[0]['subjects']==['Math','Science']
    public=public_profile({'teachers':teachers})
    assert set(public['teachers'][0])=={'id','name','subjects'}
    assert 'example.invalid' not in str(public)


@pytest.mark.asyncio
async def test_teacher_photo_requires_configured_child_and_known_teacher():
    from custom_components.casvi.panel import ws_teacher_photo
    connection=MagicMock();connection.user.is_admin=False
    with pytest.raises(Unauthorized):ws_teacher_photo(MagicMock(),connection,{'id':1})
    client=SimpleNamespace(read_teacher_photo=AsyncMock())
    c=SimpleNamespace(children={'a':'Child'},client=client,panel_profiles={'a':{'teachers':[{'id':'7'}]}})
    hass=SimpleNamespace(data={'casvi':{'account':c}})
    handler=ws_teacher_photo.__wrapped__.__wrapped__
    await handler(hass,connection,{'id':1,'entry_id':'account','child_id':'other','teacher_id':'7'})
    await handler(hass,connection,{'id':2,'entry_id':'account','child_id':'a','teacher_id':'unknown'})
    client.read_teacher_photo.assert_not_awaited()
    client.read_teacher_photo.return_value='data:image/png;base64,example'
    await handler(hass,connection,{'id':3,'entry_id':'account','child_id':'a','teacher_id':'7'})
    client.read_teacher_photo.assert_awaited_once_with({'id':'7'})


@pytest.mark.asyncio
async def test_photo_base64_is_sniffed_and_svg_or_external_sources_not_executed():
    import base64
    from custom_components.casvi.api import CasviError
    client=CasviClient('test','test');client._authenticated=AsyncMock()
    data=b'\x89PNG\r\n\x1a\nsynthetic'
    result=await client.read_teacher_photo({'_photo_source':base64.b64encode(data).decode(),'_source_id':''})
    assert result.startswith('data:image/png;base64,')
    with pytest.raises(CasviError):
        await client.read_teacher_photo({'_photo_source':'data:image/svg+xml;base64,'+base64.b64encode(b'<svg/>').decode(),'_source_id':''})
    with pytest.raises(CasviError):
        await client.read_teacher_photo({'_photo_source':'https://example.invalid/private','_source_id':''})
    client._authenticated.assert_not_awaited()


@pytest.mark.asyncio
async def test_photo_uses_fixed_authenticated_endpoint_and_checks_size():
    from custom_components.casvi.api import CasviError
    client=CasviClient('test','test');client._check=AsyncMock()
    async def chunks(size):yield b'\xff\xd8\xffsynthetic'
    response=MagicMock(status=200);response.content.iter_chunked=chunks
    context=MagicMock();context.__aenter__=AsyncMock(return_value=response);context.__aexit__=AsyncMock(return_value=False)
    client._session=MagicMock();client._session.get.return_value=context
    photo=await client.read_teacher_photo({'_source_id':'7','_photo_source':'https://example.invalid/photo'})
    assert photo.startswith('data:image/jpeg;base64,')
    assert client._session.get.call_args.args[0]=='https://intranet.casvi.es/pages/verFotos.php?tipo=usuario&id=7'
    assert client._session.get.call_args.kwargs['allow_redirects'] is False
    with pytest.raises(CasviError):client._photo_payload(b'\xff\xd8\xff'+b'x'*(2*1024*1024))


@pytest.mark.asyncio
async def test_teachers_failure_does_not_hide_rest_of_child_profile():
    from custom_components.casvi.api import CasviError
    client=CasviClient('test','test');client._login=AsyncMock();client._check=AsyncMock()
    client._request=AsyncMock(side_effect=[
        '<span id="nombreGrupo" data-id="4"></span>',
        {'status':'success','data':{'idGrupo':4,'etiquetaGrupo':'Example'}},
        [{'nombre':'Classmate'}],CasviError('Unavailable'),
        {'success':True,'data':[]},{'status':'success','data':[]},
    ])
    profile=await client.child_profile('a')
    assert profile['teachers_available'] is False
    assert profile['classmates']==[{'nombre':'Classmate'}]


@pytest.mark.asyncio
async def test_overview_refreshes_before_returning_data_only_when_requested():
    coordinator = SimpleNamespace(data=None, async_request_refresh=AsyncMock())
    hass = SimpleNamespace(data={'casvi': {'account': coordinator}})
    connection = MagicMock()
    handler = ws_overview.__wrapped__.__wrapped__
    await handler(hass, connection, {'id': 1})
    coordinator.async_request_refresh.assert_not_awaited()
    await handler(hass, connection, {'id': 2, 'refresh': True})
    coordinator.async_request_refresh.assert_awaited_once()
    connection.send_result.assert_called_with(2, [])


def test_message_excerpt_is_plain_bounded_and_optional():
    from custom_components.casvi.panel import message_excerpt, message_summary
    assert message_excerpt('<p>Hola &amp; adiós</p><script>secret()</script>') == 'Hola & adiós'
    assert message_excerpt('a' * 200) == 'a' * 177 + '…'
    assert message_summary(row(), {})['excerpt'] == ''
    assert message_summary({**row(), 'mensaje': '<b>Vista previa</b>'}, {})['excerpt'] == 'Vista previa'


def test_attachment_links_only_allow_casvi_downloads():
    from custom_components.casvi.panel import attachment_links
    result=attachment_links([{'nombre':'Example.pdf','ruta_descargar':'../download.php?id=1'},
                             {'nombre':'Bad','ruta_descargar':'javascript:alert(1)'},
                             {'nombre':'External','ruta_descargar':'https://example.com/file'}])
    assert result[0]['url']=='https://intranet.casvi.es/download.php?id=1'
    assert result[1]['url'] is None
    assert result[2]['url'] is None


@pytest.mark.asyncio
async def test_mark_read_failure_keeps_message_readable_and_pending():
    from custom_components.casvi.api import CasviError
    client=SimpleNamespace(read_message=AsyncMock(return_value={'mensaje':'Hello'}),mark_message_read=AsyncMock(side_effect=CasviError('failed')))
    c=SimpleNamespace(children={},data={'messages':[row()]},client=client,async_request_refresh=AsyncMock())
    connection=MagicMock()
    await ws_message.__wrapped__.__wrapped__(SimpleNamespace(data={'casvi':{'account':c}}),connection,{'id':1,'entry_id':'account','message_id':'1','recipient_id':'2'})
    assert connection.send_result.call_args.args[1]['read'] is False
    assert connection.send_result.call_args.args[1]['content']=='Hello'


@pytest.mark.asyncio
async def test_mark_read_uses_both_ids_and_checks_confirmation():
    from custom_components.casvi.api import CasviError
    client=CasviClient('test','test');client._login=AsyncMock();client._check=AsyncMock()
    client._request=AsyncMock(return_value={'success':True})
    await client.mark_message_read('1','2')
    client._request.assert_awaited_once_with('/controles/mensajesAdmin.php',{'accion':'marcar_leido','id_mensaje':'1','id_para':'2'})
    client._request.return_value={'success':False}
    with pytest.raises(CasviError):await client.mark_message_read('1','2')


@pytest.mark.asyncio
async def test_attachment_only_downloads_cached_account_message_attachment():
    from custom_components.casvi.panel import ws_attachment
    client = SimpleNamespace(read_attachment=AsyncMock(return_value=(b'%PDF-test', 'application/pdf')))
    coordinator = SimpleNamespace(client=client, panel_attachments={('1', '2'): [{'url':'https://intranet.casvi.es/file.pdf'}]})
    hass = SimpleNamespace(data={'casvi': {'account': coordinator}})
    connection = MagicMock()
    handler = ws_attachment.__wrapped__.__wrapped__
    message = {'id':1, 'entry_id':'account', 'message_id':'1', 'recipient_id':'2', 'index':0}
    await handler(hass, connection, message)
    assert connection.send_result.call_args.args[1]['mime'] == 'application/pdf'
    client.read_attachment.assert_awaited_once_with('https://intranet.casvi.es/file.pdf')
    client.read_attachment.reset_mock()
    for overrides in ({'entry_id':'other'}, {'recipient_id':'other'}, {'index':-1}, {'index':10}):
        await handler(hass, connection, message | overrides)
    client.read_attachment.assert_not_awaited()


def test_attachment_requires_admin():
    from custom_components.casvi.panel import ws_attachment
    connection = MagicMock()
    connection.user.is_admin = False
    with pytest.raises(Unauthorized):
        ws_attachment(MagicMock(), connection, {'id': 1})


@pytest.mark.asyncio
async def test_month_menu_scoped_account_and_plain_text():
    from custom_components.casvi.panel import ws_menu
    client = SimpleNamespace(month_menu=AsyncMock(return_value=[
        {'fecha':'2026-09-01','menu':'<p>Lentejas</p>'},
        {'fecha':'2026-10-01','menu':'Other month'},
    ]))
    hass = SimpleNamespace(data={'casvi': {'account': SimpleNamespace(client=client)}})
    connection = MagicMock()
    message = {'id':1,'entry_id':'account','year':2026,'month':9}
    await ws_menu.__wrapped__.__wrapped__(hass, connection, message)
    assert connection.send_result.call_args.args[1] == {'menus':[{'date':'2026-09-01','menu':'Lentejas'}]}
    client.month_menu.assert_awaited_once_with(2026,9)
    client.month_menu.reset_mock()
    await ws_menu.__wrapped__.__wrapped__(hass, connection, message | {'entry_id':'other'})
    client.month_menu.assert_not_awaited()
    connection.user.is_admin = False
    with pytest.raises(Unauthorized):
        ws_menu(hass,connection,message)


def test_message_attachment_indicator_uses_inbox_metadata():
    from custom_components.casvi.panel import message_summary
    assert message_summary(row(), {})['attachment_count'] == 0
    assert message_summary(row() | {'adjuntos': None}, {})['attachment_count'] == 0
    assert message_summary(row() | {'adjuntos': [{'nombre':'a.pdf'}, {'nombre':'b.png'}]}, {})['attachment_count'] == 2
