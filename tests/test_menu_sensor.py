from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo
from custom_components.casvi.sensor import CasviSensor


def sensor_for(text):
    today = datetime.now(ZoneInfo('Europe/Madrid')).date().isoformat()
    coordinator = SimpleNamespace(entry=SimpleNamespace(entry_id='account'),
                                  data={'menus':[{'fecha':today,'menu':text}]})
    return CasviSensor(coordinator, 'menu', 'Casvi comedor hoy')


def test_menu_state_is_readable_and_full_text_is_kept():
    sensor = sensor_for('<p>Lentejas</p><p>Tortilla</p>')
    assert sensor.native_value == 'Lentejas Tortilla'
    assert 'Lentejas' in sensor.extra_state_attributes['menu']
    text = 'Menú largo ' * 40
    sensor = sensor_for(text)
    assert len(sensor.native_value) <= 255
    assert sensor.native_value.endswith('…')
    assert sensor.extra_state_attributes['menu'] == text.strip()


def test_empty_or_other_day_never_shows_old_menu_as_today():
    sensor = sensor_for('')
    assert sensor.native_value == 'Sin menú publicado'
    sensor.coordinator.data['menus'] = [{'fecha':'2000-01-01','menu':'Menú antiguo'}]
    assert sensor.native_value == 'Sin menú publicado'
    assert sensor.extra_state_attributes == {'fecha':None, 'menu':''}
