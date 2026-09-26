"""Casvi integration."""
from .api import CasviClient
from .const import PLATFORMS
from .coordinator import CasviCoordinator
from .panel import async_setup_panel, async_remove_panel
from homeassistant.helpers.storage import Store


async def async_setup_entry(hass, entry):
    client = CasviClient(entry.data["username"], entry.data["password"])
    coordinator = CasviCoordinator(hass, entry, client)
    try:
        await coordinator.async_config_entry_first_refresh()
        entry.runtime_data = coordinator
        await async_setup_panel(hass)
        hass.data.setdefault("casvi", {})[entry.entry_id] = coordinator
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except BaseException:
        hass.data.get("casvi", {}).pop(entry.entry_id, None)
        async_remove_panel(hass)
        await client.close()
        raise
    entry.async_on_unload(entry.add_update_listener(_reload))
    return True


async def _reload(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass, entry):
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data.get("casvi", {}).pop(entry.entry_id, None)
        async_remove_panel(hass)
        await entry.runtime_data.client.close()
        return True
    return False


async def async_remove_entry(hass, entry):
    await Store(hass, 1, f"casvi.messages.{entry.entry_id}").async_remove()
