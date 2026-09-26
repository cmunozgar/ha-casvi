"""Authenticated, administrator-only school panel with on-demand reading."""
import asyncio
import base64
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import voluptuous as vol
from homeassistant.components import frontend, panel_custom, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import callback
from .api import CasviError, plain_text
from .calendar import calendar_events


def message_summary(row, children):
    recipients = []
    for child in row.get("alumnosReferidos") or []:
        if not isinstance(child, dict):
            continue
        ident = str(child.get("id", ""))
        label = plain_text(child.get("nombre_completo")) or children.get(ident, "")
        if not label:
            label = " ".join(plain_text(child.get(k)) for k in ("nombre", "apellido1", "apellido2")).strip()
        if label and not any(r["id"] == ident and r["name"] == label for r in recipients):
            recipients.append({"id": ident, "name": label})
    if not recipients:
        ident = str(row.get("idUsuAlumno") or "")
        label = children.get(ident) or plain_text(row.get("nombreAlumno"))
        if label:
            recipients.append({"id": ident, "name": label})
    return {"id": str(row["id"]), "id_para": str(row["idPara"]),
            "subject": plain_text(row.get("asunto")), "sender": plain_text(row.get("remitente")),
            "date": str(row.get("fechaEnvio", "")), "read": str(row.get("leido")) == "1",
            "children": recipients}


def remember_messages(coordinator, rows):
    cache = getattr(coordinator, "panel_messages", None)
    if cache is None:
        cache = coordinator.panel_messages = OrderedDict()
    for row in rows:
        key = (str(row["id"]), str(row["idPara"]))
        cache[key] = row
        cache.move_to_end(key)
    while len(cache) > 1000:
        cache.popitem(last=False)


def profile_summary(raw):
    group = raw["group"]
    documents = [{"id": str(d["id"]), "title": plain_text(d.get("titulo")),
                  "kind": "documentoGrupo", "group": str(group["idGrupo"])}
                 for d in group.get("documentos", [])]
    documents += [{"id": str(d["id"]), "title": plain_text(d.get("titulo")),
                   "kind": "documentoAlumno"} for d in raw["documents"]
                  if d.get("visiblePadre") is True or str(d.get("visiblePadre")) == "1"]
    return {
        "group": plain_text(group.get("etiquetaGrupo")), "tutor": plain_text(group.get("nombreTutor")),
        "classmates": [plain_text(r.get("nombre")) for r in raw["classmates"]],
        "documents": documents,
        "tutorials": [{"date": plain_text(t.get("fecha")), "reason": plain_text(t.get("motivo")),
                       "teacher": " ".join(plain_text(t.get(k)) for k in ("profesorNombre", "profesorApellido1", "profesorApellido2")).strip(),
                       "summary": plain_text(t.get("resumen")) if str(t.get("visiblePadre")) == "1" or t.get("visiblePadre") is True else "",
                       "plan": plain_text(t.get("planAccion")) if str(t.get("visiblePadre")) == "1" or t.get("visiblePadre") is True else ""}
                      for t in raw["tutorials"]],
    }


def summary(coordinator):
    data = coordinator.data
    today = datetime.now(ZoneInfo("Europe/Madrid")).date().isoformat()
    return {
        "entry_id": coordinator.entry.entry_id,
        "name": ", ".join(coordinator.children.values()) or "Casvi",
        "available": coordinator.last_update_success,
        "children": [{"id": ident, "name": name} for ident, name in coordinator.children.items()],
        "messages": [message_summary(r, coordinator.children) for r in data["messages"]],
        "total_messages": data["total"],
        "menu": next((plain_text(r.get("menu")) for r in data["menus"] if r.get("fecha") == today), ""),
        "date": today,
        "events": [{"child": name, "child_id": child, "title": e.summary, "start": e.start.isoformat(), "description": e.description}
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
            ), StaticPathConfig("/casvi-logo.png", str(Path(__file__).parent / "brand" / "icon.png"), False),
                StaticPathConfig("/casvi-static", str(Path(__file__).parent / "frontend"), True)])
            websocket_api.async_register_command(hass, ws_overview)
            websocket_api.async_register_command(hass, ws_message)
            websocket_api.async_register_command(hass, ws_messages)
            websocket_api.async_register_command(hass, ws_child)
            websocket_api.async_register_command(hass, ws_document)
            state["registered"] = True
        if not state.get("visible"):
            await panel_custom.async_register_panel(
                hass, frontend_url_path="colegio", webcomponent_name="casvi-school-panel",
                sidebar_title="Colegio", sidebar_icon="mdi:school-outline",
                module_url="/casvi-panel.js?v=0.3.0", require_admin=True,
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
        row = getattr(coordinator, "panel_messages", {}).get((msg["message_id"], msg["recipient_id"]))
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
        "children": message_summary(row, coordinator.children)["children"],
        "content": plain_text(detail.get("mensaje")),
        "attachments": [plain_text(a.get("nombre")) for a in (detail.get("adjuntos") or row.get("adjuntos") or [])],
    })
    # Reflect any server-side read-state changes without explicitly marking read.
    await coordinator.async_request_refresh()


@websocket_api.websocket_command({
    vol.Required("type"): "casvi/messages", vol.Required("entry_id"): str,
    vol.Optional("start", default=0): vol.All(int, vol.Range(min=0)),
    vol.Optional("length", default=20): vol.All(int, vol.Range(min=1, max=100)),
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_messages(hass, connection, msg):
    coordinator = hass.data.get("casvi", {}).get(msg["entry_id"])
    if coordinator is None:
        connection.send_error(msg["id"], "not_ready", "La cuenta no está disponible.")
        return
    try:
        page = await coordinator.client.list_messages(msg.get("start", 0), msg.get("length", 20))
    except CasviError:
        connection.send_error(msg["id"], "cannot_connect", "No se pudieron consultar los mensajes.")
        return
    remember_messages(coordinator, page["messages"])
    connection.send_result(msg["id"], {
        "messages": [message_summary(r, coordinator.children) for r in page["messages"]],
        "total": page["total"], "start": msg.get("start", 0),
    })


@websocket_api.websocket_command({vol.Required("type"): "casvi/child", vol.Required("entry_id"): str, vol.Required("child_id"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_child(hass, connection, msg):
    coordinator = hass.data.get("casvi", {}).get(msg["entry_id"])
    if coordinator is None or msg["child_id"] not in coordinator.children:
        connection.send_error(msg["id"], "not_found", "Alumno no configurado.")
        return
    try:
        result = profile_summary(await coordinator.client.child_profile(msg["child_id"]))
    except CasviError:
        connection.send_error(msg["id"], "cannot_connect", "No se pudo cargar la información del alumno.")
        return
    if not hasattr(coordinator, "panel_profiles"):
        coordinator.panel_profiles = {}
    coordinator.panel_profiles[msg["child_id"]] = result
    connection.send_result(msg["id"], result)


@websocket_api.websocket_command({
    vol.Required("type"): "casvi/document", vol.Required("entry_id"): str,
    vol.Required("child_id"): str, vol.Required("document_id"): str,
    vol.Required("kind"): vol.In(["documentoGrupo", "documentoAlumno"]),
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_document(hass, connection, msg):
    coordinator = hass.data.get("casvi", {}).get(msg["entry_id"])
    if coordinator is None or msg["child_id"] not in coordinator.children:
        connection.send_error(msg["id"], "not_found", "Alumno no configurado.")
        return
    profile = getattr(coordinator, "panel_profiles", {}).get(msg["child_id"], {})
    document = next((d for d in profile.get("documents", []) if d["id"] == msg["document_id"] and d["kind"] == msg["kind"]), None)
    if document is None:
        connection.send_error(msg["id"], "not_found", "Documento no disponible para esta ficha.")
        return
    try:
        pdf = await coordinator.client.read_document(msg["child_id"], document)
    except CasviError:
        connection.send_error(msg["id"], "cannot_connect", "No se pudo abrir el PDF. Debe ser un PDF de hasta 5 MB.")
        return
    connection.send_result(msg["id"], {"title": document["title"], "pdf": base64.b64encode(pdf).decode("ascii")})


def async_remove_panel(hass):
    if not hass.data.get("casvi") and hass.data.get("casvi_panel", {}).get("visible"):
        frontend.async_remove_panel(hass, "colegio")
        hass.data["casvi_panel"]["visible"] = False
