import os

# Usage reporting (see usageReporting.py). The key is the program key the
# trace service issued to Tidewater (program 55); it identifies the program,
# not the player, and is bundled so an install that never sets
# TIDEWATER_USAGE_REPORTING_KEY still reports. Keys ship in public source by
# design: they are identity and revocation, not secrecy.
USAGE_REPORTING_ENDPOINT_DEFAULT = "https://trace.danielstephenson.dev"
USAGE_REPORTING_KEY_DEFAULT = "G3XwvcVo0dbokS5Z1SwI6ETtf37cBhPfB5MeIp_TsYI"

# Values that switch a TIDEWATER_* boolean off. Anything else - including
# unset and empty - leaves the default in place, matching TIDEWATER_SAVE_DIR.
_FALSE_VALUES = ("0", "false", "no", "off")


def _environmentFlag(name, default):
    value = os.environ.get(name, "").strip().lower()
    if not value:
        return default
    return value not in _FALSE_VALUES


# @author Daniel McCoy Stephenson
class Config:
    def __init__(self):
        # TIDEWATER_SAVE_DIR relocates the whole save directory - a mounted
        # volume for a server install, or the Worker-side directory that the
        # Pyodide front-end mirrors to the browser's IndexedDB.
        self.dataDirectory = os.environ.get("TIDEWATER_SAVE_DIR") or "data"

        self.usageReportingEnabled = _environmentFlag(
            "TIDEWATER_USAGE_REPORTING_ENABLED", True
        )
        self.usageReportingEndpoint = (
            os.environ.get("TIDEWATER_USAGE_REPORTING_ENDPOINT", "").strip()
            or USAGE_REPORTING_ENDPOINT_DEFAULT
        )
        self.usageReportingKey = (
            os.environ.get("TIDEWATER_USAGE_REPORTING_KEY", "").strip()
            or USAGE_REPORTING_KEY_DEFAULT
        )
