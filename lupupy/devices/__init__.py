"""Init file for devices directory."""

import re
from typing import TYPE_CHECKING

import lupupy.constants as CONST

if TYPE_CHECKING:
    from lupupy.api.current.helper import LupusecApi


class LupusecDevice:
    """Class to represent each Lupusec device."""

    def __init__(self, json_obj: dict):
        """Set up Lupusec device."""
        self._json_state = json_obj
        self._device_id = json_obj.get("device_id")
        self._name = json_obj.get("name")
        self._type = json_obj.get("type")

        if self._type in CONST.TYPE_TRANSLATION:
            self._generic_type = CONST.TYPE_TRANSLATION[self._type]
        else:
            self._generic_type = "generic_type_unknown"

        self._status = json_obj.get("status")

        if not self._name:
            self._name = self._generic_type + " " + self.device_id

    def get_value(self, name: str) -> str:
        """Get a value from the json object."""

        return self._json_state.get(name)

    def refresh(self, api: "LupusecApi") -> dict | None:
        """Refresh a device."""
        if self.type == CONST.ALARM_TYPE:
            response = api.get_panel()
            self.update(response)
            return response

        # The original XT1 reports its power switches through a dedicated
        # endpoint, every other device comes from the sensor list.
        if self.type == CONST.TYPE_POWER_SWITCH:
            response = api.get_power_switches()
        else:
            response = api.get_sensors()

        for device in response:
            if device["device_id"] == self._device_id:
                self.update(device)
                return device

        return None

    def set_status(self, on: bool, api: "LupusecApi") -> bool:
        """Switch the device on or off."""
        return api.switch(self.device_id, on)

    def update(self, json_state: dict) -> None:
        """Update the device from a panel response."""
        self._json_state.update(json_state)

    @property
    def status(self) -> str:
        """Shortcut to get the generic status of a device."""
        return self.get_value("status")

    @property
    def level(self) -> str:
        """Shortcut to get the generic level of a device."""
        return self.get_value("level")

    # The panel reports the signal strength as a localisation placeholder
    # followed by the raw value, e.g. '{WEB_MSG_STRONG}\t9'.
    RSSI_PATTERN = re.compile(r"\{WEB_MSG_[A-Z_]+\}\s*(\d+)")

    def _is_faulty(self, name: str) -> bool:
        """Evaluate one of the panel's '_ok' fields.

        The panel reports '1' while the device is healthy, so a field it does
        not send is treated as healthy as well.
        """
        value = self.get_value(name)
        if value is None:
            return False
        return str(value) == "0"

    @property
    def battery_low(self) -> bool:
        """Is battery level low."""
        return self._is_faulty("battery_ok")

    @property
    def no_response(self) -> bool:
        """Is the device responding."""
        return self.rssi == 0

    @property
    def out_of_order(self) -> bool:
        """Is the device out of order."""
        return self._is_faulty("cond_ok")

    @property
    def tampered(self) -> bool:
        """Has the device been tampered with."""
        return self._is_faulty("tamper_ok")

    @property
    def bypassed(self) -> bool:
        """Is the device bypassed.

        A bypassed device does not trigger an alarm while the panel is armed.
        """
        return str(self.get_value("bypass")) == "1"

    @property
    def rssi(self) -> int | None:
        """Signal strength of the device, 0 when the panel hears nothing.

        None where there is nothing to measure: devices that only transmit
        when they are used report N/A, and the panel's own rssi field is the
        interference it sees rather than a signal it receives.
        """
        match = self.RSSI_PATTERN.search(str(self.get_value("rssi")))
        return int(match.group(1)) if match else None

    @property
    def area(self) -> str:
        """Get the area this device belongs to."""
        return self.get_value("area")

    @property
    def zone(self) -> str:
        """Get the zone of this device."""
        return self.get_value("zone")

    @property
    def name(self) -> str:
        """Get the name of this device."""
        return self._name

    @property
    def type(self) -> str:
        """Get the type of this device."""
        return self._type

    @property
    def generic_type(self) -> str:
        """Get the generic type of this device."""
        return self._generic_type

    @property
    def device_id(self) -> str:
        """Get the device id."""
        return self._device_id

    @property
    def desc(self) -> str:
        """Get a short description of the device."""
        return f"{self.name} (ID: {self.device_id}) - {self.type} - {self.status}"
