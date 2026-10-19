"""Constants for the Janitza UMG 604-PRO integration."""

DOMAIN = "janitza_umg604"

CONF_UNIT_ID = "unit_id"

DEFAULT_PORT = 502
DEFAULT_UNIT_ID = 1
DEFAULT_SCAN_INTERVAL = 10  # seconds

MANUFACTURER = "Janitza"
MODEL = "UMG 604-PRO"

# "Frequently required measured values" block: float32, big-endian, holding
# registers (function code 3). 19000..19121 fits into a single read (max 125).
BLOCK_START = 19000
BLOCK_COUNT = 122
