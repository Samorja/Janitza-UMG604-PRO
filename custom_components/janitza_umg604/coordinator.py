"""Data update coordinator for the Janitza UMG 604-PRO."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import JanitzaClient, JanitzaConnectionError
from .const import BLOCK_COUNT, BLOCK_START, DOMAIN

_LOGGER = logging.getLogger(__name__)


class JanitzaCoordinator(DataUpdateCoordinator[dict[int, float | None]]):
    """Polls the measured-values block on a fixed interval."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: JanitzaClient,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> dict[int, float | None]:
        try:
            return await self.client.read_floats(BLOCK_START, BLOCK_COUNT)
        except JanitzaConnectionError as err:
            raise UpdateFailed(f"Error reading UMG 604-PRO: {err}") from err
