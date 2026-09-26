"""Read-only Casvi web client; no session material is persisted or logged."""
from __future__ import annotations

import asyncio
import json
import re
from datetime import date
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

    async def _request(self, path, data=None, *, multipart=False, text=False):
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
