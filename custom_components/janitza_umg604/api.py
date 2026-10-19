"""Modbus TCP client for the Janitza UMG 604-PRO."""

from __future__ import annotations

import asyncio
import inspect
import math
import struct

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException


class JanitzaConnectionError(Exception):
    """Raised when the device cannot be reached or returns an error."""


class JanitzaClient:
    """Thin async wrapper that reads float32 register blocks."""

    def __init__(self, host: str, port: int, unit_id: int) -> None:
        self._client = AsyncModbusTcpClient(host, port=port, timeout=5)
        self._unit_id = unit_id
        self._lock = asyncio.Lock()
        # pymodbus 3.10 renamed the "slave" keyword to "device_id".
        params = inspect.signature(self._client.read_holding_registers).parameters
        self._unit_kwarg = "device_id" if "device_id" in params else "slave"

    async def read_floats(self, start: int, count: int) -> dict[int, float | None]:
        """Read `count` registers from `start`, keyed by the start register of each float."""
        async with self._lock:
            if not self._client.connected and not await self._client.connect():
                raise JanitzaConnectionError("Unable to connect to device")
            try:
                result = await self._client.read_holding_registers(
                    start, count=count, **{self._unit_kwarg: self._unit_id}
                )
            except ModbusException as err:
                self._client.close()
                raise JanitzaConnectionError(str(err)) from err
            if result.isError():
                raise JanitzaConnectionError(f"Modbus error response: {result}")

        regs = result.registers
        values: dict[int, float | None] = {}
        for offset in range(0, count - 1, 2):
            raw = struct.pack(">HH", regs[offset], regs[offset + 1])
            value = struct.unpack(">f", raw)[0]
            values[start + offset] = value if math.isfinite(value) else None
        return values

    def close(self) -> None:
        """Close the TCP connection."""
        self._client.close()
