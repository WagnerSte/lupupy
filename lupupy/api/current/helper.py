"""Helpers for the XT1 Plus and its successors.

LupusecApi does not talk HTTP itself. It holds the facade as self.rest,
where every public method is one REST action named after it, and works
with the answers: it rewrites field names, normalises states, reads the
event log and works around what the panel does differently from its
documentation. Which actions a helper uses is said in its docstring;
whether an action is documented is said where it is defined.

The first XT1 has a helper of its own in lupupy.api.legacy.helper, which
builds on this one and overrides only what differs.
"""

import logging
import pickle
import time
from pathlib import Path

import lupupy.constants as CONST
from lupupy.api.current import vendor_api
from lupupy.api.data_models import (
    LupusecAlarmMode,
    LupusecModel,
    LupusecModelType,
)
from lupupy.api.current.undocumented_api import UndocumentedApi
from lupupy.exceptions import LupusecNotSupportedException

_LOGGER = logging.getLogger(__name__)
home = str(Path.home())


# Sent with every switching command: a socket ignores the command without
# pd, and empty means "until switched again".
SWITCH_FOR_GOOD = ""

# Refreshing each device asks for the whole list; answering those from a
# short-lived copy keeps the panel from being asked once per device.
CACHE_SECONDS = 2.0


def _load_history_cache() -> list:
    try:
        return pickle.load(open(home + "/" + CONST.HISTORY_CACHE_NAME, "rb"))
    except FileNotFoundError as e:
        _LOGGER.debug(e)
        pickle.dump([], open(home + "/" + CONST.HISTORY_CACHE_NAME, "wb"))
        return []


class LupusecApi:
    """What the library asks of an XT1 Plus or one of its successors."""

    generation = LupusecModelType.XT1Plus_2_3_4

    def __init__(self, rest: UndocumentedApi, model: LupusecModel):
        """Work with a facade for the model the user configured."""
        self.rest = rest
        self.model = model
        self._history_cache = _load_history_cache()
        self._cache: dict[str, tuple[float, list[dict]]] = {}

    def _cached(self, key: str, fetch) -> list[dict]:
        """Answer from a copy younger than CACHE_SECONDS, or fetch anew."""
        stamp, value = self._cache.get(key, (0.0, None))
        if value is None or time.time() - stamp > CACHE_SECONDS:
            value = fetch()
            self._cache[key] = (time.time(), value)
        return value

    def get_power_switches(self) -> list[dict]:
        """Nothing: switches and shutters are part of the device list here."""
        return []

    def get_sensors(self) -> list[dict]:
        """Every device with a device_id and a normalised status, via deviceListGet.

        An open contact reads 1 and a closed one "Geschlossen".
        """
        return self._cached("sensors", self._read_sensors)

    def _read_sensors(self) -> list[dict]:
        sensors = []
        for device in self.rest.device_list_get()["senrows"]:
            if "openClose" in device:
                device["status"] = device.pop("openClose")
            device["device_id"] = device.pop("sid")
            device.pop("cond")
            sensors.append(self._normalise_status(device))
        return sensors

    @staticmethod
    def _normalise_status(device: dict) -> dict:
        if device["status"] in ("{WEB_MSG_DC_OPEN}", CONST.STATUS_OPEN):
            device["status"] = 1
        if device["status"] in ("{WEB_MSG_DC_CLOSE}", "0", ""):
            device["status"] = "Geschlossen"
        return device

    def get_panel(self) -> dict:
        """The panel as a device: its condition and the mode of each area.

        Uses panelCondGet, and the event log to tell whether an alarm went
        off since it was last read: an alarm is a new row of type "3".
        """
        panel = self.rest.panel_cond_get()["updates"]
        self._read_modes(panel)
        panel["device_id"] = CONST.ALARM_DEVICE_ID
        panel["type"] = CONST.ALARM_TYPE
        panel["name"] = CONST.ALARM_NAME

        for histrow in self.get_history():
            if histrow in self._history_cache:
                continue
            if self._alarm_went_off(histrow):
                panel["mode"] = CONST.STATE_ALARM_TRIGGERED
            self._history_cache.append(histrow)
            pickle.dump(
                self._history_cache,
                open(home + "/" + CONST.HISTORY_CACHE_NAME, "wb"),
            )
        return panel

    @staticmethod
    def _read_modes(panel: dict) -> None:
        """Turn the placeholder of the mode into a mode name."""
        panel["mode"] = CONST.XT2_MODES_TO_TEXT[panel.pop("mode_a1")]

    @staticmethod
    def _alarm_went_off(row: dict) -> bool:
        return row[CONST.HISTORY_ALARM_COLUMN_XT2] == CONST.MODE_ALARM_TRIGGERED_XT2

    def get_history(self) -> list:
        """The raw rows of the event log, via recordListGet."""
        return self.rest.record_list_get()[CONST.HISTORY_HEADER_XT2]

    def set_mode(self, mode: LupusecAlarmMode) -> bool:
        """Arm or disarm the panel, via panelCondPost."""
        mode_value = self.get_alarm_mode_value(mode)
        if mode_value == -1:
            raise LupusecNotSupportedException(f"{mode} cannot be set on this panel")
        return self._succeeded(self.rest.panel_cond_post(1, mode_value))

    def get_alarm_mode_value(self, mode: LupusecAlarmMode) -> int:
        """The value panelCondPost takes for a mode, or -1."""
        return {
            LupusecAlarmMode.Disarmed: vendor_api.MODE_DISARM,
            LupusecAlarmMode.Armed: vendor_api.MODE_ARM,
            LupusecAlarmMode.Home: vendor_api.MODE_HOME1,
        }.get(mode, -1)

    def switch(self, device_id: str, on: bool) -> bool:
        """Switch a socket or relay, via deviceSwitchPSSPost."""
        return self._succeeded(
            self.rest.device_switch_pss_post(
                device_id,
                switch=vendor_api.SWITCH_ON if on else vendor_api.SWITCH_OFF,
                pd=SWITCH_FOR_GOOD,
            )
        )

    def move_shutter(self, device_id: str, direction: int) -> bool:
        """Move a shutter up or down, or stop it, via deviceSwitchPSSPost.

        direction is SHUTTER_UP, SHUTTER_DOWN or SHUTTER_STOP from
        lupupy.api.current.vendor_api.
        """
        return self._succeeded(
            self.rest.device_switch_pss_post(
                device_id, switch=direction, pd=SWITCH_FOR_GOOD
            )
        )

    @staticmethod
    def _succeeded(result: dict) -> bool:
        """Whether a Result says the panel did what it was asked."""
        if str(result.get("result")) == "1":
            return True
        _LOGGER.warning("The panel refused: %s", result.get("message"))
        return False

