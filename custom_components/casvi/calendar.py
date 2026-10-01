"""School calendar from the events actually returned by Casvi."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .api import plain_text

SCHOOL_TZ = ZoneInfo("Europe/Madrid")


def calendar_events(rows):
    result = []
    seen = set()
    for row in rows:
        try:
            start = datetime.fromisoformat(row["start"])
        except (KeyError, ValueError, TypeError):
            continue
        if start.tzinfo is None:
            start = start.replace(tzinfo=SCHOOL_TZ)
        key = (str(row.get("id", "")), start.isoformat())
        if key in seen:
            continue
        seen.add(key)
        # API provides no end time. Use a documented one-minute display interval.
        end = start + timedelta(minutes=1)
        props = row.get("extendedProps") or {}
        result.append(CalendarEvent(
            start=start, end=end, summary=plain_text(row.get("title")) or plain_text(props.get("tipo")) or "Evento Casvi",
            description=plain_text(props.get("texto") or props.get("descripcion")),
        ))
    return sorted(result, key=lambda event: event.start)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(CasviCalendar(entry.runtime_data, child, name)
                       for child, name in entry.runtime_data.children.items())


class CasviCalendar(CoordinatorEntity, CalendarEntity):
    def __init__(self, coordinator, child, name):
        super().__init__(coordinator)
        name = name.split()[0] if name.strip() else name
        self.child = child
        self._attr_name = f"Casvi agenda {name}"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_agenda_{child}"
        self._attr_supported_features = 0

    def _events(self):
        return calendar_events(self.coordinator.data["agenda"].get(self.child, []))

    @property
    def event(self):
        now = datetime.now(SCHOOL_TZ)
        return next((event for event in self._events() if event.end > now), None)

    async def async_get_events(self, hass, start_date, end_date):
        return [event for event in self._events()
                if event.end > start_date and event.start < end_date]
