"""Casvi integration."""
from .api import CasviClient
from .const import PLATFORMS
from .coordinator import CasviCoordinator


async def async_setup_entry(hass, entry):
    client = CasviClient(entry.data["username"], entry.data["password"])
    coordinator = CasviCoordinator(hass, entry, client)
    try:
        await coordinator.async_config_entry_first_refresh()
        entry.runtime_data = coordinator
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except BaseException:
        await client.close()
        raise
    entry.async_on_unload(entry.add_update_listener(_reload))
    return True


async def _reload(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass, entry):
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        await entry.runtime_data.client.close()
        return True
    return False
