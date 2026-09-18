"""The helper for the first XT1.

It builds on the helper of the XT1 Plus and its successors and overrides
only what differs: the first XT1 speaks an API of its own, reached through
lupupy.api.legacy.undocumented_legacy_api. What it cannot do raises
LupusecNotSupportedException.
"""

import logging

import lupupy.constants as CONST
from lupupy.api.current.helper import LupusecApi
from lupupy.api.data_models import (
    LupusecAlarmMode,
    LupusecModel,
    LupusecModelType,
)
from lupupy.api.legacy import undocumented_legacy_api
from lupupy.api.legacy.undocumented_legacy_api import UndocumentedLegacyApi
from lupupy.exceptions import LupusecNotSupportedException

_LOGGER = logging.getLogger(__name__)


class LegacyLupusecApi(LupusecApi):
    """What the library asks of a first XT1.

    Only what differs from the XT1 Plus is here. What the first XT1 cannot
    do raises LupusecNotSupportedException, for the calling application to
    handle. None of it was verified in this version of the library, for
    want of a first XT1 to try it on.
    """

    generation = LupusecModelType.XT1_Legacy

    def __init__(self, rest: UndocumentedLegacyApi, model: LupusecModel):
        """Work with the first XT1's facade, which wants a login first."""
        super().__init__(rest, model)
        self.rest.sensor_list_get()
        self.rest.login_post()

    def get_power_switches(self) -> list[dict]:
        """The power switches, which the XT1 lists apart, via pssStatusGet."""
        return self._cached("power_switches", self._read_power_switches)

    def _read_power_switches(self) -> list[dict]:
        powerSwitches = []
        counter = 1
        forms = self.rest.pss_status_get()["forms"]
        for pss in forms:
            if forms[pss]["ready"] == 1:
                powerSwitches.append(
                    {
                        "status": forms[pss]["pssonoff"],
                        # The switches have no id of their own. Numbering
                        # them from the device count made the id move
                        # whenever the panel gained a device.
                        "device_id": f"pss{counter}",
                        "type": CONST.TYPE_POWER_SWITCH,
                        "name": forms[pss]["name"],
                    }
                )
            else:
                _LOGGER.debug("Pss skipped, not active")
            counter += 1
        return powerSwitches

    def _read_sensors(self) -> list[dict]:
        """The sensors via sensorListGet, whose id is no and state cond."""
        sensors = []
        for device in self.rest.sensor_list_get()["senrows"]:
            device["status"] = device.pop("cond")
            device["device_id"] = device.pop("no")
            sensors.append(self._normalise_status(device))
        return sensors

    @staticmethod
    def _read_modes(panel: dict) -> None:
        """The XT1 reports its single mode as text in mode_st."""
        panel["mode"] = panel.pop("mode_st")

    @staticmethod
    def _alarm_went_off(row: dict) -> bool:
        return CONST.MODE_ALARM_TRIGGERED in row[CONST.HISTORY_ALARM_COLUMN]

    def get_history(self) -> list:
        """The raw rows of the event log, via historyGet."""
        return self.rest.history_get()[CONST.HISTORY_HEADER]

    def set_mode(self, mode: LupusecAlarmMode) -> bool:
        """Arm or disarm the panel, via panelCondPost without an area."""
        mode_value = self.get_alarm_mode_value(mode)
        if mode_value == -1:
            raise LupusecNotSupportedException(
                f"{mode} cannot be set on the first XT1"
            )
        return self._succeeded(self.rest.panel_cond_post(mode_value))

    def get_alarm_mode_value(self, mode: LupusecAlarmMode) -> int:
        """The value the XT1's panelCondPost takes for a mode, or -1."""
        return {
            LupusecAlarmMode.Disarmed: undocumented_legacy_api.MODE_DISARM,
            LupusecAlarmMode.Armed: undocumented_legacy_api.MODE_ARM,
            LupusecAlarmMode.Home: undocumented_legacy_api.MODE_HOME,
        }.get(mode, -1)
