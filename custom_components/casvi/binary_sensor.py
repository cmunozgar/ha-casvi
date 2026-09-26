"""Per-child activities from the school timetable."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .schedule import activity_today

TZ = ZoneInfo('Europe/Madrid')


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(CasviActivity(entry.runtime_data, child, name, activity)
                       for child,name in entry.runtime_data.children.items()
                       for activity in ('pool','pe'))


class CasviActivity(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, child, name, activity):
        super().__init__(coordinator)
        self.child, self.activity = child, activity
        self._attr_unique_id = f'{coordinator.entry.entry_id}_{child}_{activity}_today'
        label = 'Piscina' if activity == 'pool' else 'Educación física'
        self._attr_name = f'Casvi {name} {label} hoy'
        self._attr_icon = 'mdi:swim' if activity == 'pool' else 'mdi:run'

    def _schedule(self):
        return (self.coordinator.data or {}).get('schedules', {}).get(self.child)

    @property
    def available(self):
        return super().available and self._schedule() is not None

    @property
    def is_on(self):
        schedule = self._schedule()
        return activity_today(schedule['rows'], datetime.now(TZ).date(), self.activity) if schedule else None

    @property
    def extra_state_attributes(self):
        schedule = self._schedule()
        return {'fecha':datetime.now(TZ).date().isoformat(), 'origen':'Horario semanal del PDF',
                'incluye_psicomotricidad':self.activity == 'pe',
                'estado_detalle': 'Horario no disponible' if schedule is None else
                    'EF/NAT: actividad por confirmar' if self.is_on is None else 'Horario habitual',
                'calendario_lectivo_aplicado':False}

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self._school_date = datetime.now(TZ).date()
        @callback
        def check_date(now):
            today = now.astimezone(TZ).date()
            if today != self._school_date:
                self._school_date = today
                self.async_write_ha_state()
        self.async_on_remove(async_track_time_interval(self.hass, check_date, timedelta(minutes=1)))
