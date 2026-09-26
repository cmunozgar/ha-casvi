"""Read-only Casvi web client; no session material is persisted or logged."""
from __future__ import annotations

import asyncio
import base64
import binascii
import json
import re
from urllib.parse import urlencode
from datetime import date, timedelta
from html import unescape
from html.parser import HTMLParser

import aiohttp

BASE_URL = "https://intranet.casvi.es"


class CasviError(Exception):
    """Communication or response contract error."""


class CasviAuthError(CasviError):
    """Credentials rejected or session cannot be established."""


class SessionExpired(CasviError):
    """Session ended while reading data."""


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1
        if tag in ("br", "p", "div", "li"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)
        if tag in ("p", "div", "li"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def plain_text(value):
    parser = _Text()
    parser.feed(str(value or "").replace("\\r\\n", "\n"))
    return re.sub(r"\n{3,}", "\n\n", unescape("".join(parser.parts))).strip()


def discover_children(html):
    """Read only the account's family navigation; never guess student IDs."""
    result = {}
    pattern = r'href=[\"\x27]#hijoMenu-(\d+)[\"\x27][\s\S]*?<span[^>]*class=[\"\x27][^\"\x27]*area-padre-hijo-nombre[^\"\x27]*[\"\x27][^>]*>([\s\S]*?)</span>'
    allowed = set(re.findall(r"agenda\.php\?idUsuAlumno=(\d+)", html))
    for ident, label in re.findall(pattern, html):
        if ident in allowed:
            result[ident] = plain_text(label)
    for ident in sorted(allowed):
        result.setdefault(ident, f"Alumno {ident}")
    return result


class _GroupPage(HTMLParser):
    group_id = None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id") == "nombreGrupo" and values.get("data-id", "").isdigit():
            self.group_id = values["data-id"]


class CasviClient:
    def __init__(self, username, password, *, base_url=BASE_URL):
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip("/")
        self._session = None
        self._lock = asyncio.Lock()

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def _request(self, path, data=None, *, multipart=False, text=False, allow_list=False):
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"X-Requested-With": "XMLHttpRequest", "Origin": self.base_url,
                         "Referer": self.base_url + "/", "Accept": "application/json, */*"},
                cookie_jar=aiohttp.CookieJar(),
            )
        body = data
        if multipart:
            body = aiohttp.FormData()
            for key, value in data.items():
                body.add_field(key, str(value), content_type="text/plain")
        try:
            async with self._session.request(
                "POST" if data is not None else "GET", self.base_url + path,
                data=body, allow_redirects=False,
            ) as response:
                raw = await response.text()
                if response.status in (301, 302, 303, 307, 308, 401):
                    raise SessionExpired("Session redirected or expired")
                if response.status >= 400:
                    raise CasviError(f"HTTP {response.status}")
        except (aiohttp.ClientError, TimeoutError) as err:
            raise CasviError("Cannot connect to Casvi") from err
        if raw.strip().strip('"') == "caducado" or (path != "/" and 'id="login_form"' in raw):
            raise SessionExpired("Session expired")
        if text:
            return raw
        try:
            payload = json.loads(raw)
        except ValueError as err:
            raise CasviError("Unexpected non-JSON response") from err
        if allow_list and isinstance(payload, list):
            return payload
        if not isinstance(payload, dict):
            raise CasviError("Unexpected response structure")
        if payload.get("status") == "caducado":
            raise SessionExpired("Session expired")
        return payload

    async def _check(self):
        data = await self._request("/controles/sesion.php", {"accion": "check"})
        if data.get("status") != "ok":
            raise SessionExpired("Session not active")

    async def _login(self):
        await self.close()
        await self._request("/", text=True)
        result = await self._request("/controles/usuarios.php", {
            "accion": "login", "usuario": self.username, "pass": self.password,
        }, multipart=True)
        if result.get("status") != "success":
            raise CasviAuthError("Login rejected")
        try:
            await self._check()
        except SessionExpired as err:
            raise CasviAuthError("Login did not establish a session") from err

    async def _authenticated(self, operation):
        async with self._lock:
            for attempt in range(2):
                try:
                    if self._session is None:
                        await self._login()
                    else:
                        await self._check()
                    result = await operation()
                    # Some endpoints return success with empty data when unauthenticated.
                    await self._check()
                    return result
                except SessionExpired as err:
                    if attempt:
                        raise CasviAuthError("Session remains invalid") from err
                    await self.close()
            raise CasviAuthError("Session unavailable")

    async def authenticate(self):
        async def load():
            html = await self._request("/pages/escritorio.php", text=True)
            return discover_children(html)
        return await self._authenticated(load)

    @staticmethod
    def _data(result):
        if result.get("success") is not True and result.get("status") != "success":
            raise CasviError("Casvi rejected the read request")
        return result.get("data")

    async def child_profile(self, child_id):
        async def load():
            parser = _GroupPage()
            parser.feed(await self._request("/pages/infoGrupoDelAlumno.php?" + urlencode({"idAlumno": child_id}), text=True))
            group = {}
            classmates = []
            teachers = []
            teachers_available = True
            if parser.group_id:
                group = self._data(await self._request("/controles/grupos.php", {
                    "accion": "get_detalle_info_grupo_alumno", "idAlumno": str(child_id),
                    "idGrupo": parser.group_id,
                }, multipart=True))
                classmates = await self._request("/controles/grupos.php", {
                    "accion": "mostrar_alumnos_grupo", "id": parser.group_id, "soloNombre": "1",
                }, multipart=True, allow_list=True)
                if isinstance(classmates, dict):
                    classmates = classmates.get("data")
                try:
                    response = await self._request("/controles/asignaturas.php", {
                        "accion": "mostrar_asignaturas_y_profesores_grupo", "id": parser.group_id,
                    }, multipart=True)
                    teachers = response.get("data")
                    if not isinstance(teachers, list) or response.get("success") is False or response.get("status") == "error":
                        raise CasviError("Invalid teachers list")
                except SessionExpired:
                    raise
                except CasviError:
                    teachers = []
                    teachers_available = False
            tutorials = self._data(await self._request("/controles/gestionTutorias.php", {
                "accion": "getTutoriasByAlumno", "idAlumno": str(child_id),
            }, multipart=True))
            documents = await self._request("/controles/documentosAlumno.php", {
                "accion": "mostrar_documentos_alumno_by_id", "id": str(child_id),
                "incluirOtroCentro": "1",
            }, multipart=True, allow_list=True)
            if isinstance(documents, dict):
                documents = self._data(documents)
            if not isinstance(group, dict) or not all(isinstance(v, list) for v in (classmates, tutorials, documents)):
                raise CasviError("Unexpected student response")
            return {"group": group, "classmates": classmates, "tutorials": tutorials,
                    "documents": documents, "teachers": teachers, "teachers_available": teachers_available}
        return await self._authenticated(load)

    @staticmethod
    def _photo_payload(data):
        if len(data) > 2 * 1024 * 1024:
            raise CasviError("Photo exceeds 2 MB")
        if data.startswith(b"\xff\xd8\xff"):
            mime = "image/jpeg"
        elif data.startswith(b"\x89PNG\r\n\x1a\n"):
            mime = "image/png"
        elif data[:6] in (b"GIF87a", b"GIF89a"):
            mime = "image/gif"
        elif data.startswith(b"RIFF") and data[8:12] == b"WEBP":
            mime = "image/webp"
        else:
            raise CasviError("Photo unavailable")
        return "data:" + mime + ";base64," + base64.b64encode(data).decode("ascii")

    async def read_teacher_photo(self, teacher):
        """Use only group-authorized photo data or the fixed Casvi photo endpoint."""
        source = teacher.get("_photo_source")
        if isinstance(source, str) and source and len(source) <= 3 * 1024 * 1024:
            encoded = source.split(",", 1)[1] if source.startswith("data:image/") and ";base64," in source else source
            if not source.startswith(("http:", "https:")):
                try:
                    data = base64.b64decode("".join(encoded.split()), validate=True)
                    return self._photo_payload(data)
                except (ValueError, binascii.Error, CasviError):
                    pass
        ident = teacher.get("_source_id", "")
        if not ident.isdigit() or int(ident) <= 0:
            raise CasviError("Photo unavailable")
        async def load():
            try:
                async with self._session.get(self.base_url + "/pages/verFotos.php?" + urlencode({"tipo": "usuario", "id": ident}), allow_redirects=False) as response:
                    if response.status in (301, 302, 303, 307, 308, 401):
                        raise SessionExpired("Session expired")
                    if response.status >= 400:
                        raise CasviError("Photo unavailable")
                    photo = bytearray()
                    async for chunk in response.content.iter_chunked(65536):
                        photo.extend(chunk)
                        if len(photo) > 2 * 1024 * 1024:
                            raise CasviError("Photo exceeds 2 MB")
            except (aiohttp.ClientError, TimeoutError) as err:
                raise CasviError("Cannot download photo") from err
            if b'login_form' in photo[:4096] or b'caducado' in photo[:256]:
                raise SessionExpired("Session expired")
            return self._photo_payload(bytes(photo))
        return await self._authenticated(load)

    async def read_document(self, child_id, document):
        """Download only the known viewer endpoint, with a bounded PDF payload."""
        params = {"tipo": document["kind"], "doc": document["id"]}
        if document["kind"] == "documentoGrupo":
            params.update(grupo=document["group"], idAlumno=child_id)
        elif document["kind"] == "documentoAlumno":
            params["Alumno"] = child_id
        else:
            raise CasviError("Unsupported document")
        async def load():
            try:
                async with self._session.get(self.base_url + "/pages/verDocumento.php?" + urlencode(params), allow_redirects=False) as response:
                    if response.status in (301, 302, 303, 307, 308, 401):
                        raise SessionExpired("Session expired")
                    if response.status >= 400:
                        raise CasviError("Document unavailable")
                    result = bytearray()
                    async for chunk in response.content.iter_chunked(65536):
                        result.extend(chunk)
                        if len(result) > 5 * 1024 * 1024:
                            raise CasviError("PDF exceeds 5 MB")
            except (aiohttp.ClientError, TimeoutError) as err:
                raise CasviError("Cannot download document") from err
            if not result.startswith(b"%PDF-"):
                if b'login_form' in result or b'caducado' in result:
                    raise SessionExpired("Session expired")
                raise CasviError("Document is not a PDF")
            return bytes(result)
        return await self._authenticated(load)

    async def list_messages(self, start=0, length=20):
        """Read one authenticated server-side page, without fetching bodies."""
        if not isinstance(start, int) or start < 0 or not isinstance(length, int) or not 1 <= length <= 100:
            raise CasviError("Invalid pagination")
        async def load():
            result = await self._request("/controles/mensajesAdmin.php", {
                "accion": "listar_mensajes_recibidos", "start": str(start),
                "length": str(length), "search": "", "noLeidos": "0",
            })
            rows = self._data(result)
            if not isinstance(rows, list):
                raise CasviError("Invalid messages list")
            try:
                total = int(result["total"])
            except (KeyError, ValueError, TypeError) as err:
                raise CasviError("Invalid messages total") from err
            return {"messages": rows, "total": total}
        return await self._authenticated(load)

    async def read_message(self, message_id, recipient_id):
        """Fetch a body only after an explicit user action, never while polling."""
        async def load():
            detail = self._data(await self._request("/controles/mensajesAdmin.php", {
                "accion": "ver_mensaje_recibido", "id_mensaje": str(message_id),
                "id_para": str(recipient_id),
            }))
            if not isinstance(detail, dict):
                raise CasviError("Invalid message detail")
            return detail
        return await self._authenticated(load)

    async def snapshot(self, children, today: date, message_limit=50):
        async def load():
            received = await self._request("/controles/mensajesAdmin.php", {
                "accion": "listar_mensajes_recibidos", "start": "0",
                "length": str(message_limit), "search": "", "noLeidos": "0",
            })
            messages = self._data(received)
            if not isinstance(messages, list):
                raise CasviError("Invalid messages list")
            menu = await self._request("/controles/comedor.php", {
                "accion": "obtener_menus_mes", "anio": str(today.year), "mes": str(today.month),
            }, multipart=True)
            if str(menu.get("error")) != "0" or not isinstance(menu.get("menus"), list):
                raise CasviError("Invalid menu response")
            # Include adjacent months when yesterday/tomorrow cross a boundary.
            months = {(day.year, day.month) for day in
                      (today - timedelta(days=1), today + timedelta(days=1))}
            for year, month in sorted(months - {(today.year, today.month)}):
                adjacent = await self._request("/controles/comedor.php", {
                    "accion": "obtener_menus_mes", "anio": str(year), "mes": str(month),
                }, multipart=True)
                if str(adjacent.get("error")) != "0" or not isinstance(adjacent.get("menus"), list):
                    raise CasviError("Invalid adjacent menu response")
                menu["menus"].extend(adjacent["menus"])
            agenda = {}
            for child in children:
                response = await self._request("/controles/agendaEvento.php", {
                    "accion": "get_eventos_alumno_especifico", "idAlumno": str(child),
                })
                rows = self._data(response)
                if not isinstance(rows, list):
                    raise CasviError("Invalid agenda response")
                agenda[str(child)] = rows
            # Only already-read messages: avoid changing unread status until verified.
            latest = messages[0] if messages else None
            detail = None
            if latest and str(latest.get("leido")) == "1":
                detail = self._data(await self._request("/controles/mensajesAdmin.php", {
                    "accion": "ver_mensaje_recibido", "id_mensaje": str(latest["id"]),
                    "id_para": str(latest["idPara"]),
                }))
                if not isinstance(detail, dict):
                    raise CasviError("Invalid message detail")
            try:
                total = int(received["total"])
            except (KeyError, ValueError, TypeError) as err:
                raise CasviError("Invalid messages total") from err
            return {"messages": messages, "total": total, "detail": detail,
                    "menus": menu["menus"], "agenda": agenda}
        return await self._authenticated(load)
