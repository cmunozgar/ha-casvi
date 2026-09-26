"""Authenticated, administrator-only school panel with on-demand reading."""
import asyncio
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import voluptuous as vol
from homeassistant.components import frontend, panel_custom, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import callback
from .api import CasviError, plain_text
from .calendar import calendar_events


def summary(coordinator):
    data = coordinator.data
    today = datetime.now(ZoneInfo("Europe/Madrid")).date().isoformat()
    return {
        "entry_id": coordinator.entry.entry_id,
        "name": ", ".join(coordinator.children.values()) or "Casvi",
        "available": coordinator.last_update_success,
        "messages": [{"id": str(r["id"]), "id_para": str(r["idPara"]),
                      "subject": plain_text(r.get("asunto")), "sender": plain_text(r.get("remitente")),
                      "date": str(r.get("fechaEnvio", "")), "read": str(r.get("leido")) == "1"}
                     for r in data["messages"]],
        "menu": next((plain_text(r.get("menu")) for r in data["menus"] if r.get("fecha") == today), ""),
        "date": today,
        "events": [{"child": name, "title": e.summary, "start": e.start.isoformat(), "description": e.description}
                   for child, name in coordinator.children.items()
                   for e in calendar_events(data["agenda"].get(child, []))
                   if e.start.date().isoformat() >= today],
        "notifications": bool(coordinator.entry.options.get("notify_targets")),
    }


async def async_setup_panel(hass):
    state = hass.data.setdefault("casvi_panel", {})
    async with state.setdefault("lock", asyncio.Lock()):
        if not state.get("registered"):
            await hass.http.async_register_static_paths([StaticPathConfig(
                "/casvi-panel.js", str(Path(__file__).parent / "frontend" / "casvi-panel.js"), False,
            )])
            websocket_api.async_register_command(hass, ws_overview)
            websocket_api.async_register_command(hass, ws_message)
            state["registered"] = True
        if not state.get("visible"):
            await panel_custom.async_register_panel(
                hass, frontend_url_path="colegio", webcomponent_name="casvi-school-panel",
                sidebar_title="Colegio", sidebar_icon="mdi:school-outline",
                module_url="/casvi-panel.js?v=0.2.0", require_admin=True,
            )
            state["visible"] = True


@websocket_api.websocket_command({vol.Required("type"): "casvi/overview"})
@websocket_api.require_admin
@callback
def ws_overview(hass, connection, msg):
    entries = hass.data.get("casvi", {})
    connection.send_result(msg["id"], [summary(c) for c in entries.values() if c.data])


@websocket_api.websocket_command({
    vol.Required("type"): "casvi/message", vol.Required("entry_id"): str,
    vol.Required("message_id"): str, vol.Required("recipient_id"): str,
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_message(hass, connection, msg):
    coordinator = hass.data.get("casvi", {}).get(msg["entry_id"])
    if coordinator is None or not coordinator.data:
        connection.send_error(msg["id"], "not_ready", "La cuenta no está disponible.")
        return
    # Only messages present in this account's validated inbox can be requested.
    row = next((r for r in coordinator.data["messages"]
                if str(r["id"]) == msg["message_id"] and str(r["idPara"]) == msg["recipient_id"]), None)
    if row is None:
        connection.send_error(msg["id"], "not_found", "El mensaje ya no está entre los recientes. Ábrelo en la intranet.")
        return
    try:
        detail = await coordinator.client.read_message(row["id"], row["idPara"])
    except CasviError:
        connection.send_error(msg["id"], "cannot_connect", "No se pudo abrir el mensaje. Inténtalo de nuevo.")
        return
    connection.send_result(msg["id"], {
        "subject": plain_text(row.get("asunto")), "sender": plain_text(row.get("remitente")),
        "content": plain_text(detail.get("mensaje")),
        "attachments": [plain_text(a.get("nombre")) for a in (detail.get("adjuntos") or row.get("adjuntos") or [])],
    })
    # Reflect any server-side read-state changes without explicitly marking read.
    await coordinator.async_request_refresh()


def async_remove_panel(hass):
    if not hass.data.get("casvi") and hass.data.get("casvi_panel", {}).get("visible"):
        frontend.async_remove_panel(hass, "colegio")
        hass.data["casvi_panel"]["visible"] = False
