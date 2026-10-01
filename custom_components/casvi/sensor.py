"""Read-only summary sensors."""
from datetime import datetime
from zoneinfo import ZoneInfo
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .api import plain_text


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(CasviSensor(entry.runtime_data, key, name) for key, name in [
        ("total", "Casvi mensajes recibidos"),
        ("unread", "Casvi mensajes no leídos recientes"),
        ("latest", "Casvi último mensaje"),
        ("menu", "Casvi comedor hoy"),
    ])
    coordinator = entry.runtime_data
    async_add_entities([CasviNewEvents(coordinator)] +
                       [CasviNewEvents(coordinator, child) for child in coordinator.children])
    async_add_entities([CasviUnreadWidget(coordinator, slot) for slot in range(3)] +
                       [entity for child in coordinator.children
                        for entity in (CasviUnreadWidget(coordinator, child=child, count=True),
                                       CasviUnreadWidget(coordinator, child=child))])


class CasviSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, name):
        super().__init__(coordinator)
        self.key = key
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"
        self._attr_icon = "mdi:food" if key == "menu" else "mdi:email-outline"

    def _menu(self):
        today = datetime.now(ZoneInfo("Europe/Madrid")).date().isoformat()
        return next((m for m in self.coordinator.data["menus"] if m["fecha"] == today), None)

    @property
    def native_value(self):
        data = self.coordinator.data
        if self.key == "total":
            return data["total"]
        if self.key == "unread":
            return sum(str(m.get("leido")) == "0" for m in data["messages"])
        if self.key == "latest":
            return plain_text(data["messages"][0].get("asunto"))[:250] if data["messages"] else "Sin mensajes"
        menu = self._menu()
        text = " ".join(plain_text(menu.get("menu")).split()) if menu else ""
        if not text:
            return "Sin menú publicado"
        return text if len(text) <= 255 else text[:254].rstrip() + "…"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if self.key == "menu":
            menu = self._menu()
            return {"fecha": menu["fecha"] if menu else None,
                    "menu": plain_text(menu["menu"]) if menu else ""}
        if self.key == "unread":
            return {"mensajes_examinados": len(data["messages"]), "total_buzon": data["total"]}
        if self.key != "latest" or not data["messages"]:
            return {}
        item = data["messages"][0]
        return {"id": item.get("id"), "fecha": item.get("fechaEnvio"),
                "remitente": plain_text(item.get("remitente")),
                "leido": str(item.get("leido")) == "1",
                "contenido": plain_text((data["detail"] or {}).get("mensaje")),
                "contenido_disponible": data["detail"] is not None,
                "adjuntos": [plain_text(a.get("nombre")) for a in item.get("adjuntos", [])]}


def unread_rows(coordinator, child=None):
    """Only explicit recipients; never attribute general mail to a child."""
    result = []
    for row in coordinator.data['messages']:
        if str(row.get('leido')) != '0':
            continue
        recipients = {str(c.get('id')) for c in row.get('alumnosReferidos') or [] if isinstance(c, dict)}
        if row.get('idUsuAlumno'):
            recipients.add(str(row['idUsuAlumno']))
        if child is None or child in recipients:
            result.append(row)
    return sorted(result, key=lambda r:str(r.get('fechaEnvio') or ''), reverse=True)


class CasviUnreadWidget(CoordinatorEntity, SensorEntity):
    """Stable widget slots, populated without fetching message bodies."""
    def __init__(self, coordinator, slot=0, child=None, count=False):
        super().__init__(coordinator)
        self.slot, self.child, self.count = slot, child, count
        scope = coordinator.children[child].split()[0] if child and coordinator.children[child].strip() else ''
        label = 'Mensajes no leídos recientes' if count else f'Mensaje no leído {slot+1}'
        self._attr_name = f'Casvi {scope} {label}'.replace('  ',' ')
        self._attr_unique_id = f'{coordinator.entry.entry_id}_widget_{child or "account"}_{"count" if count else slot}'
        self._attr_icon = 'mdi:email-multiple-outline' if count else 'mdi:email-alert-outline'

    @property
    def native_value(self):
        rows = unread_rows(self.coordinator, self.child)
        if self.count:
            return len(rows)
        return (plain_text(rows[self.slot].get('asunto')) or 'Sin asunto')[:250] if len(rows)>self.slot else 'Sin mensajes pendientes'

    @property
    def extra_state_attributes(self):
        from urllib.parse import urlencode
        rows = unread_rows(self.coordinator, self.child)
        attrs = {'mensajes_examinados':len(self.coordinator.data['messages']),
                 'pendientes_recientes':len(rows), 'total_buzon':self.coordinator.data['total'],
                 'alcance':'Mensajes recientes consultados', 'url':'/colegio'}
        if self.count or len(rows)<=self.slot:
            return attrs
        row = rows[self.slot]
        names = [plain_text(c.get('nombre_completo') or c.get('nombre')) or self.coordinator.children.get(str(c.get('id')), '')
                 for c in row.get('alumnosReferidos') or [] if isinstance(c, dict)]
        if not any(names):
            names = [self.coordinator.children.get(str(row.get('idUsuAlumno')), '') or plain_text(row.get('nombreAlumno'))]
        attrs.update({'id':str(row['id']), 'id_para':str(row['idPara']),
                      'fecha':str(row.get('fechaEnvio') or ''), 'remitente':plain_text(row.get('remitente')),
                      'alumnos':[name for name in names if name], 'asunto':plain_text(row.get('asunto')),
                      'url':'/colegio?'+urlencode({'entry':self.coordinator.entry.entry_id,'message':row['id'],'recipient':row['idPara']})})
        return attrs


class CasviNewEvents(CoordinatorEntity, SensorEntity):
    """Cumulative newly detected events, excluding the initial history."""
    _attr_icon = 'mdi:calendar-plus'

    def __init__(self, coordinator, child=None):
        super().__init__(coordinator)
        self.child = child
        name = coordinator.children[child].split()[0] if child and coordinator.children[child].strip() else ''
        self._attr_name = f'Casvi {name} Eventos nuevos'.replace('  ', ' ')
        self._attr_unique_id = f'{coordinator.entry.entry_id}_new_events_{child or "account"}'

    @property
    def available(self):
        return super().available and 'new_events' in (self.coordinator.data or {})

    @property
    def native_value(self):
        counts = (self.coordinator.data or {}).get('new_events', {})
        return counts.get(self.child, 0) if self.child else sum(counts.values())

    @property
    def extra_state_attributes(self):
        return {'alcance': 'Acumulado desde la primera sincronización; no indica eventos sin leer',
                'url': '/colegio', 'alumno_id': self.child}
