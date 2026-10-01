"""Authenticated, administrator-only school panel with on-demand reading."""
import asyncio
import base64
import hashlib
from urllib.parse import urljoin, urlsplit, urlunsplit
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import voluptuous as vol
from homeassistant.components import frontend, panel_custom, websocket_api
from homeassistant.components.http import StaticPathConfig
from .api import menu_text
from .api import CasviError, plain_text, message_text
from .calendar import calendar_events
from .message_format import message_nodes


def attachment_links(attachments):
    result = []
    for attachment in attachments:
        if not isinstance(attachment, dict):
            continue
        url = urlsplit(urljoin('https://intranet.casvi.es/pages/mensajes.php', str(attachment.get('ruta_descargar') or '')))
        safe = (bool(attachment.get('ruta_descargar')) and url.scheme in ('http','https')
                and url.netloc.lower() == 'intranet.casvi.es' and not url.username)
        result.append({'name':plain_text(attachment.get('nombre')) or 'Adjunto',
                       'url':urlunsplit(('https',url.netloc,url.path,url.query,url.fragment)) if safe else None})
    return result


def message_excerpt(value):
    text = " ".join(plain_text(value).split())
    return text if len(text) <= 180 else text[:177].rstrip() + "…"


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
            "attachment_count": len(row.get("adjuntos")) if isinstance(row.get("adjuntos"), list) else 0,
            "children": recipients, "excerpt": message_excerpt(row.get("mensaje"))}


def panel_message_summary(coordinator, row):
    result = message_summary(row, coordinator.children)
    key = (str(row["id"]), str(row["idPara"]))
    result["excerpt"] = result["excerpt"] or getattr(coordinator, "panel_excerpts", {}).get(key, "")
    return result


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


def teachers_summary(rows):
    teachers = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = plain_text(row.get("profesor"))
        source_id = str(row.get("idProfesor") or "")
        subject = plain_text(row.get("asignatura"))
        if not name and (not source_id.isdigit() or int(source_id) <= 0):
            continue
        ident = source_id if source_id.isdigit() and int(source_id) > 0 else "name-" + hashlib.sha256(name.casefold().encode()).hexdigest()[:24]
        teacher = teachers.setdefault(ident, {"id": ident, "name": name or "Profesor sin nombre", "subjects": [],
                                              "_source_id": source_id, "_photo_source": None})
        if subject and subject not in teacher["subjects"]:
            teacher["subjects"].append(subject)
        if not teacher["_photo_source"] and isinstance(row.get("foto"), str):
            teacher["_photo_source"] = row["foto"]
    return list(teachers.values())


def public_profile(profile):
    return {**profile, "teachers": [{k: v for k, v in t.items() if not k.startswith("_")} for t in profile["teachers"]]}


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
        "teachers": teachers_summary(raw.get("teachers", [])),
        "teachers_available": raw.get("teachers_available", True),
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
        "children": [{"id": ident, "name": name,
                      "given_name": next((plain_text(child.get("nombre"))
                          for message in data["messages"] for child in (message.get("alumnosReferidos") or [])
                          if isinstance(child, dict) and str(child.get("id")) == ident and child.get("nombre")), "")}
                     for ident, name in coordinator.children.items()],
        "messages": [panel_message_summary(coordinator, r) for r in data["messages"]],
        "total_messages": data["total"],
        "menu": next((menu_text(r.get("menu")) for r in data["menus"] if r.get("fecha") == today), ""),
        "menus": [{"date": (datetime.fromisoformat(today).date() + timedelta(days=offset)).isoformat(),
                   "menu": next((menu_text(r.get("menu")) for r in data["menus"]
                                 if r.get("fecha") == (datetime.fromisoformat(today).date() + timedelta(days=offset)).isoformat()), "")}
                  for offset in (-1, 0, 1)],
        "date": today,
        "events": [{"child": name, "child_id": child, "title": e.summary, "start": e.start.isoformat(), "description": e.description}
                   for child, name in coordinator.children.items()
                   for e in calendar_events(data["agenda"].get(child, []))],
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
            websocket_api.async_register_command(hass, ws_attachment)
            websocket_api.async_register_command(hass, ws_menu)
            websocket_api.async_register_command(hass, ws_teacher_photo)
            state["registered"] = True
        if not state.get("visible"):
            await panel_custom.async_register_panel(
                hass, frontend_url_path="colegio", webcomponent_name="casvi-school-panel",
                sidebar_title="Colegio", sidebar_icon="mdi:school-outline",
                module_url="/casvi-panel.js?v=0.4.0", require_admin=True,
            )
            state["visible"] = True


@websocket_api.websocket_command({vol.Required("type"): "casvi/overview", vol.Optional("refresh", default=False): bool})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_overview(hass, connection, msg):
    entries = hass.data.get("casvi", {})
    if msg.get("refresh", False):
        await asyncio.gather(*(c.async_request_refresh() for c in entries.values()))
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
    read_confirmed = str(row.get('leido')) == '1'
    if not read_confirmed:
        try:
            await coordinator.client.mark_message_read(row['id'], row['idPara'])
            row['leido'] = '1'
            read_confirmed = True
        except CasviError:
            pass
    if not hasattr(coordinator, "panel_excerpts"):
        coordinator.panel_excerpts = OrderedDict()
    key = (str(row["id"]), str(row["idPara"]))
    coordinator.panel_excerpts[key] = message_excerpt(detail.get("mensaje"))
    coordinator.panel_excerpts.move_to_end(key)
    while len(coordinator.panel_excerpts) > 1000:
        coordinator.panel_excerpts.popitem(last=False)
    attachments = attachment_links(detail.get("adjuntos") or row.get("adjuntos") or [])
    if not hasattr(coordinator, "panel_attachments"):
        coordinator.panel_attachments = OrderedDict()
    coordinator.panel_attachments[key] = attachments
    coordinator.panel_attachments.move_to_end(key)
    while len(coordinator.panel_attachments) > 100:
        coordinator.panel_attachments.popitem(last=False)
    connection.send_result(msg["id"], {
        "excerpt": coordinator.panel_excerpts[key],
        "read": read_confirmed,
        "date": str(row.get("fechaEnvio", "")),
        "subject": plain_text(row.get("asunto")), "sender": plain_text(row.get("remitente")),
        "children": message_summary(row, coordinator.children)["children"],
        "content": message_text(detail.get("mensaje")),
        "content_nodes": message_nodes(detail.get("mensaje")),
        "attachments": attachments,
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
        "messages": [panel_message_summary(coordinator, r) for r in page["messages"]],
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
        raw = await coordinator.profiles.read(msg["child_id"]) if hasattr(coordinator, "profiles") else await coordinator.client.child_profile(msg["child_id"])
        result = profile_summary(raw)
    except CasviError:
        connection.send_error(msg["id"], "cannot_connect", "No se pudo cargar la información del alumno.")
        return
    if not hasattr(coordinator, "panel_profiles"):
        coordinator.panel_profiles = {}
    coordinator.panel_profiles[msg["child_id"]] = result
    schedule = (coordinator.data or {}).get('schedules', {}).get(msg['child_id'])
    if schedule:
        result['schedule'] = {'rows': schedule['rows']}
    connection.send_result(msg["id"], public_profile(result))


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


@websocket_api.websocket_command({
    vol.Required("type"): "casvi/teacher_photo", vol.Required("entry_id"): str,
    vol.Required("child_id"): str, vol.Required("teacher_id"): str,
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_teacher_photo(hass, connection, msg):
    coordinator = hass.data.get("casvi", {}).get(msg["entry_id"])
    if coordinator is None or msg["child_id"] not in coordinator.children:
        connection.send_error(msg["id"], "not_found", "Alumno no configurado.")
        return
    profile = getattr(coordinator, "panel_profiles", {}).get(msg["child_id"], {})
    teacher = next((t for t in profile.get("teachers", []) if t["id"] == msg["teacher_id"]), None)
    if teacher is None:
        connection.send_error(msg["id"], "not_found", "Profesor no disponible para esta ficha.")
        return
    try:
        photo = await coordinator.client.read_teacher_photo(teacher)
    except CasviError:
        connection.send_error(msg["id"], "unavailable", "Foto no disponible.")
        return
    connection.send_result(msg["id"], {"photo": photo})


def async_remove_panel(hass):
    if not hass.data.get("casvi") and hass.data.get("casvi_panel", {}).get("visible"):
        frontend.async_remove_panel(hass, "colegio")
        hass.data["casvi_panel"]["visible"] = False


@websocket_api.websocket_command({
    vol.Required("type"): "casvi/attachment", vol.Required("entry_id"): str,
    vol.Required("message_id"): str, vol.Required("recipient_id"): str,
    vol.Required("index"): vol.All(int, vol.Range(min=0)),
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_attachment(hass, connection, msg):
    coordinator = hass.data.get("casvi", {}).get(msg["entry_id"])
    attachments = getattr(coordinator, "panel_attachments", {}).get((msg["message_id"], msg["recipient_id"]), [])
    index = msg["index"]
    if index < 0 or index >= len(attachments) or not attachments[index].get('url'):
        connection.send_error(msg['id'], 'not_found', 'Adjunto no disponible para este mensaje.')
        return
    try:
        data, mime = await coordinator.client.read_attachment(attachments[index]['url'])
    except CasviError:
        connection.send_error(msg['id'], 'cannot_connect', 'Vista previa disponible para imágenes y PDF de hasta 5 MB.')
        return
    connection.send_result(msg['id'], {'data': base64.b64encode(data).decode('ascii'), 'mime': mime})


@websocket_api.websocket_command({
    vol.Required('type'): 'casvi/menu', vol.Required('entry_id'): str,
    vol.Required('year'): vol.All(int, vol.Range(min=2000, max=2100)),
    vol.Required('month'): vol.All(int, vol.Range(min=1, max=12)),
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_menu(hass, connection, msg):
    coordinator = hass.data.get('casvi', {}).get(msg['entry_id'])
    if coordinator is None:
        connection.send_error(msg['id'], 'not_found', 'Cuenta no disponible.')
        return
    try:
        rows = await coordinator.client.month_menu(msg['year'], msg['month'])
    except CasviError:
        connection.send_error(msg['id'], 'cannot_connect', 'No se pudo cargar el menú del mes.')
        return
    prefix = f"{msg['year']:04d}-{msg['month']:02d}-"
    connection.send_result(msg['id'], {'menus': [
        {'date': str(row.get('fecha', '')), 'menu': menu_text(row.get('menu'))}
        for row in rows if str(row.get('fecha', '')).startswith(prefix)
    ]})
