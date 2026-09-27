"""A single serialized poll for the account."""
from datetime import datetime, timedelta
import logging
from zoneinfo import ZoneInfo

from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .notifications import MessageNotifications
from .schedule import ScheduleReader
from .profiles import ProfileCache

from .api import CasviAuthError, CasviError
from .const import DOMAIN, DEFAULT_INTERVAL


class CasviCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, client):
        super().__init__(hass, logging.getLogger(__name__), name=DOMAIN,
                         config_entry=entry,
                         update_interval=timedelta(minutes=entry.options.get("interval", DEFAULT_INTERVAL)))
        self.client = client
        self.entry = entry
        self.children = entry.data["children"]
        self.notifications = MessageNotifications(hass, entry)
        self.profiles = ProfileCache(hass, client, entry.entry_id)
        self.schedules = ScheduleReader(hass, client, entry.entry_id, self.profiles)

    async def _async_update_data(self):
        try:
            data = await self.client.snapshot(
                self.children, datetime.now(ZoneInfo("Europe/Madrid")).date(),
                self.entry.options.get("message_limit", 50),
            )
            data['schedules'] = {}
            today = datetime.now(ZoneInfo("Europe/Madrid")).date()
            for child in self.children:
                try:
                    data['schedules'][child] = await self.schedules.read(child, today)
                except CasviAuthError:
                    raise
                except Exception:
                    # One unreadable PDF must not disable messages or another child.
                    data['schedules'][child] = None
                    logging.getLogger(__name__).debug("School activity schedule unavailable")
            try:
                await self.notifications.process(data["messages"])
            except (OSError, HomeAssistantError):
                logging.getLogger(__name__).warning("Could not persist or deliver Casvi notifications")
            return data
        except CasviAuthError as err:
            raise ConfigEntryAuthFailed("Casvi login needs attention") from err
        except CasviError as err:
            raise UpdateFailed(str(err)) from err
