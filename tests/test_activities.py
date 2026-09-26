from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from custom_components.casvi.schedule import activity_today, ScheduleReader
from custom_components.casvi.binary_sensor import CasviActivity


def rows(subject):
    return [{'subjects':[subject]*5}]


@pytest.mark.parametrize('subject,pool,pe', [('NATACIÓN',True,False),('PSICOMOTRICIDAD',False,True),('E. FÍSICA',False,True),('EF/NAT',None,None),('LENGUA',False,False)])
def test_activity_mapping(subject,pool,pe):
    assert activity_today(rows(subject),date(2026,9,28),'pool') is pool
    assert activity_today(rows(subject),date(2026,9,28),'pe') is pe
    assert activity_today(rows(subject),date(2026,9,26),'pool') is False


def test_missing_schedule_unavailable_per_child():
    c=SimpleNamespace(entry=SimpleNamespace(entry_id='account'),last_update_success=True,data={'schedules':{'a':None,'b':{'rows':rows('NATACIÓN')}}})
    assert not CasviActivity(c,'a','Child','pool').available
    assert CasviActivity(c,'a','Child','pool').is_on is None
    assert CasviActivity(c,'b','Child','pool').available
    assert CasviActivity(c,'b','Child','pool').unique_id != CasviActivity(c,'a','Child','pool').unique_id


@pytest.mark.asyncio
async def test_schedule_cached_daily_and_failure_not_cached():
    client=SimpleNamespace(child_profile=AsyncMock(return_value={'group':{'idGrupo':1,'documentos':[{'id':2,'titulo':'Horario de clase'}]}}),read_document=AsyncMock(return_value=b'pdf'))
    hass=SimpleNamespace(async_add_executor_job=AsyncMock(return_value=rows('NATACIÓN')))
    reader=ScheduleReader(hass,client)
    await reader.read('a',date(2026,9,28))
    await reader.read('a',date(2026,9,28))
    client.read_document.assert_awaited_once()
    reader.cache.clear()
    hass.async_add_executor_job.side_effect=ValueError('bad pdf')
    with pytest.raises(ValueError):await reader.read('a',date(2026,9,29))
    with pytest.raises(ValueError):await reader.read('a',date(2026,9,29))
    assert client.read_document.await_count==3


@pytest.mark.asyncio
async def test_persistent_schedule_survives_restart_and_reparses_only_on_force():
    from unittest.mock import patch
    client=SimpleNamespace(child_profile=AsyncMock(return_value={'group':{'idGrupo':1,'documentos':[{'id':2,'titulo':'Horario'}]}}),read_document=AsyncMock(return_value=b'pdf'))
    hass=SimpleNamespace(async_add_executor_job=AsyncMock(return_value=rows('PSICOMOTRICIDAD')))
    store=SimpleNamespace(async_load=AsyncMock(return_value=None),async_save=AsyncMock())
    with patch('custom_components.casvi.schedule.Store',return_value=store):
        first=ScheduleReader(hass,client,'account')
        await first.read('a',date(2026,9,28))
        store.async_load.return_value=first.cache
        second=ScheduleReader(hass,client,'account')
        await second.read('a',date(2026,9,29))
        client.read_document.assert_awaited_once()
        await second.refresh(['a'])
        await second.read('a',date(2026,9,29))
        assert client.read_document.await_count==2
        client.child_profile.side_effect=OSError('offline')
        assert (await second.read('a',date(2026,9,30)))['rows']==rows('PSICOMOTRICIDAD')
