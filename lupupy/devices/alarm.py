"""Lupusec alarm device."""

import logging

from typing import TYPE_CHECKING

from lupupy.api.data_models import LupusecAlarmMode
from lupupy.devices.switch import LupusecDevice, LupusecSwitch

if TYPE_CHECKING:
    from lupupy.api.current.helper import LupusecApi

_LOGGER = logging.getLogger(__name__)


class LupusecAlarm(LupusecSwitch):
    """Class to represent the Lupusec alarm as a device."""

    def __init__(self, json_obj: dict, area: str = "1"):
        """Set up Lupusec alarm device."""
        LupusecSwitch.__init__(self, json_obj)
        self._area = area

    def set_mode(self, mode: LupusecAlarmMode, api: "LupusecApi") -> bool:
        """Set the mode of the area this device stands for."""
        if not api.set_mode(mode, area=int(self._area)):
            _LOGGER.warning("The panel did not accept %s", mode)
            return False

        self._json_state["mode"] = mode.value
        _LOGGER.info("Mode set to: %s", mode)
        return True

    def set_home(self, api: "LupusecApi") -> bool:
        """Arm Lupusec to home mode."""
        return self.set_mode(LupusecAlarmMode.Home, api)

    def set_away(self, api: "LupusecApi") -> bool:
        """Arm Lupusec to armed mode."""
        return self.set_mode(LupusecAlarmMode.Armed, api)

    def set_standby(self, api: "LupusecApi") -> bool:
        """Arm Lupusec to stay mode."""
        return self.set_mode(LupusecAlarmMode.Disarmed, api)

    def refresh(self, api: "LupusecApi") -> bool:
        """Refresh the alarm device."""
        response_object = LupusecDevice.refresh(self, api)
        return response_object

    def switch_on(self, api: "LupusecApi") -> bool:
        """Arm the area."""
        return self.set_mode(LupusecAlarmMode.Armed, api)

    def switch_off(self, api: "LupusecApi") -> bool:
        """Disarm the area."""
        return self.set_standby(api)

    @property
    def is_on(self) -> bool:
        """Is alarm armed."""
        return self.mode in (LupusecAlarmMode.Home, LupusecAlarmMode.Armed)

    @property
    def is_standby(self) -> bool:
        """Is alarm in standby mode."""
        return self.mode == LupusecAlarmMode.Disarmed

    @property
    def is_home(self) -> bool:
        """Is alarm in home mode."""
        return self.mode == LupusecAlarmMode.Home

    @property
    def is_away(self) -> bool:
        """Is alarm in away mode."""
        return self.mode == LupusecAlarmMode.Armed

    @property
    def is_alarm_triggered(self) -> bool:
        """Is alarm in alarm triggered mode."""
        return self.mode == LupusecAlarmMode.AlarmTriggered

    @property
    def mode(self) -> LupusecAlarmMode:
        """Get alarm mode."""
        mode_value = self.get_value("mode")
        try:
            return LupusecAlarmMode(mode_value)
        except ValueError:
            _LOGGER.error("Unknown mode: %s", mode_value)
        return LupusecAlarmMode.Unknown

    @property
    def mode_area2(self) -> LupusecAlarmMode:
        """Mode of the panel's second area."""
        try:
            return LupusecAlarmMode(self.get_value("mode_area2"))
        except ValueError:
            return LupusecAlarmMode.Unknown

    @property
    def status(self) -> str:
        """To match existing property."""
        return self.mode.value

    @property
    def battery(self) -> bool:
        """Whether the panel runs on its backup battery."""
        return self.mains_power_lost

    @property
    def mains_power_lost(self) -> bool:
        """Whether the panel has lost its mains power supply."""
        return self._is_faulty("ac_activation_ok")

    @property
    def radio_interference(self) -> bool:
        """Whether the panel sees interference on its radio."""
        return self._is_faulty("interference_ok")

    @property
    def gsm_signal_lost(self) -> bool:
        """Whether the panel has lost its GSM signal."""
        return self._is_faulty("sig_gsm_ok")

    @property
    def contact_open(self) -> bool:
        """Whether at least one door or window contact is open.

        The panel reports this inverted, as "0" while a contact is open.
        """
        return str(self.get_value("dc_ex")) == "0"

