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
        return "Disponible" if self._menu() else "Sin menú publicado"

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
