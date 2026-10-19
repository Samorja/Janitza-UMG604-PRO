"""The Janitza UMG 604-PRO integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant

from .api import JanitzaClient
from .const import CONF_UNIT_ID, DEFAULT_SCAN_INTERVAL
from .coordinator import JanitzaCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

type JanitzaConfigEntry = ConfigEntry[JanitzaCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: JanitzaConfigEntry) -> bool:
    """Set up a UMG 604-PRO from a config entry."""
    client = JanitzaClient(
        entry.data[CONF_HOST], entry.data[CONF_PORT], entry.data[CONF_UNIT_ID]
    )
    coordinator = JanitzaCoordinator(
        hass,
        entry,
        client,
        entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        client.close()
        raise

    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: JanitzaConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        entry.runtime_data.client.close()
    return unloaded


async def _async_update_listener(hass: HomeAssistant, entry: JanitzaConfigEntry) -> None:
    """Reload when options (scan interval) change."""
    await hass.config_entries.async_reload(entry.entry_id)
