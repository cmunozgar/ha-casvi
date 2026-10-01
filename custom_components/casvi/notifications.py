"""Persist discovery and pending deliveries; never notify the initial inbox."""
import hashlib
import logging
from urllib.parse import urlencode
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.storage import Store


def message_key(row):
    return hashlib.sha256(f"{row['id']}:{row['idPara']}".encode()).hexdigest()


class MessageNotifications:
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self.store = Store(hass, 1, f"casvi.messages.{entry.entry_id}")
        self.state = None

    async def process(self, rows):
        if self.state is None:
            self.state = await self.store.async_load()
        targets = self.entry.options.get("notify_targets", []) if self.entry.options.get("notify_messages", True) else []
        if self.state is None:
            self.state = {"seen": [], "baseline": max((str(r.get("fechaEnvio", "")) for r in rows), default=""), "pending": {}}
            self.state["seen"] = [message_key(r) for r in rows]
            await self.store.async_save(self.state)
            return
        seen = set(self.state["seen"])
        for row in rows:
            key = message_key(row)
            if key in seen:
                continue
            seen.add(key)
            # Expanding the recent-message window must not notify old history.
            if str(row.get("fechaEnvio", "")) <= self.state["baseline"]:
                continue
            for target in targets:
                self.state["pending"][f"{key}:{target}"] = {
                    "target": target, "id": str(row["id"]), "id_para": str(row["idPara"]),
                    "key": key, "attempts": 0,
                }
        self.state["seen"] = sorted(seen)
        # Persist before sending; a restart retains pending work.
        await self.store.async_save(self.state)
        for ident, item in list(self.state["pending"].items()):
            target = item["target"]
            if target not in targets or not target.startswith("mobile_app_"):
                del self.state["pending"][ident]
                continue
            query = urlencode({"entry": self.entry.entry_id, "message": item["id"], "recipient": item["id_para"]})
            url = f"/colegio?{query}"
            try:
                await self.hass.services.async_call("notify", target, {
                    "title": "Colegio · Casvi", "message": "Tienes un nuevo mensaje. Toca para leerlo.",
                    "data": {"url": url, "clickAction": url,
                             "tag": f"casvi-{self.entry.entry_id}-{item['key']}",
                             "group": "casvi"},
                }, blocking=True)
            except HomeAssistantError:
                item["attempts"] += 1
                if item["attempts"] >= 3:
                    logging.getLogger(__name__).warning("Casvi notification delivery failed after three attempts")
                    del self.state["pending"][ident]
            else:
                del self.state["pending"][ident]
            await self.store.async_save(self.state)
