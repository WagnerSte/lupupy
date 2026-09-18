"""Init for Lupusec module."""

import logging
from pathlib import Path

import lupupy.constants as CONST
from lupupy.api.data_models import (
    LupusecAlarmMode,
    LupusecModel,
    LupusecModelType,
)
from lupupy.api import connect
from lupupy.devices import LupusecDevice
from lupupy.devices.alarm import LupusecAlarm
from lupupy.devices.binary_sensor import LupusecBinarySensor
from lupupy.devices.cover import LupusecCover
from lupupy.devices.switch import LupusecSwitch

_LOGGER = logging.getLogger(__name__)

home = str(Path.home())


class Lupusec:
    """Class to represent the Lupusec alarm system."""

    def __init__(
        self,
        username: str,
        password: str,
        ip_address: str,
        model: LupusecModel,
        get_devices: bool = False,
    ):
        """Set up the Lupusec alarm system.

        model is the panel as it says on the device. The library does not
        find it out by itself.
        """
        self.api = connect(username, password, ip_address, model)
        self._devices = None
        self._panel = self.api.get_panel()

        if get_devices:
            self._devices = self.get_devices()
        else:
            self._devices = None

    def get_devices(
        self, refresh: bool = False, generic_type: list[str] = None
    ) -> list:
        """Get all devices from Lupusec."""
        _LOGGER.info("Updating all devices...")

        if refresh or self._devices is None:
            if self._devices is None:
                self._devices = {}

            self._update_devices()
            self._handle_panel()
            self._handle_power_switches()

        if generic_type:
            return [
                device
                for device in self._devices.values()
                if device.type in generic_type
            ]

        return list(self._devices.values())

    def get_device(self, device_id: str, refresh: bool = False) -> LupusecDevice:
        """Get a single device."""
        if self._devices is None:
            self.get_devices()
            refresh = False

        device = self._devices.get(device_id)

        if device and refresh:
            device.refresh(self.api)

        return device

    def get_alarm(self, area: str = "1", refresh: bool = False) -> LupusecAlarm:
        """Shortcut method to get the alarm device."""
        if self._devices is None:
            self.get_devices()
            refresh = False

        return self.get_device(CONST.ALARM_DEVICE_ID, refresh)

    @property
    def model(self) -> LupusecModel:
        """The panel as configured."""
        return self.api.model

    @property
    def generation(self) -> LupusecModelType:
        """The web API the configured panel speaks."""
        return self.api.generation

    def set_mode(self, mode: LupusecAlarmMode) -> bool:
        """Arm or disarm the panel."""
        return self.api.set_mode(mode)

    def get_history(self) -> list:
        """Get the event history of the panel."""
        return self.api.get_history()

    def _newDevice(self, deviceJson: dict) -> None | LupusecDevice:
        """Create new device object for the given type."""
        type_tag = deviceJson.get("type")

        if not type_tag:
            _LOGGER.info("Device has no type")

        if (
            type_tag in CONST.TYPE_OPENING
            or type_tag in CONST.TYPE_MOTION
            or type_tag in CONST.TYPE_SENSOR
            or type_tag in CONST.TYPE_SIREN
            or type_tag in CONST.TYPE_KEYPAD
        ):
            return LupusecBinarySensor(deviceJson)
        elif type_tag in CONST.TYPE_SWITCH:
            return LupusecSwitch(deviceJson)
        elif type_tag in CONST.TYPE_COVER:
            return LupusecCover(deviceJson)
        elif type_tag in CONST.TYPE_ACCESSORY:
            return LupusecDevice(deviceJson)
        else:
            _LOGGER.info("Device is not known")
        return None

    def _update_devices(self) -> None:
        """Update devices from the API."""
        responseObject = self.api.get_sensors()

        for deviceJson in responseObject:
            device = self._devices.get(deviceJson["device_id"])
            if device:
                device.update(deviceJson)
            else:
                device = self._newDevice(deviceJson)
                if not device:
                    _LOGGER.info("Device is unknown")
                    continue
                self._devices[device.device_id] = device

    def _handle_panel(self) -> None:
        """Handle the Lupusec panel as an armable device."""
        panelJson = self.api.get_panel()
        _LOGGER.debug("Get the panel in get_devices: %s", panelJson)

        self._panel.update(panelJson)

        alarmDevice = self._devices.get(CONST.ALARM_DEVICE_ID)
        if alarmDevice:
            alarmDevice.update(panelJson)
        else:
            alarmDevice = LupusecAlarm(panelJson)
            self._devices[CONST.ALARM_DEVICE_ID] = alarmDevice

    def _handle_power_switches(self) -> None:
        """Add the power switches the panel lists apart from its devices.

        Only the first XT1 does; on later panels the list is empty.
        """
        for deviceJson in self.api.get_power_switches():
            device = self._devices.get(deviceJson["device_id"])
            if device:
                device.update(deviceJson)
            else:
                device = self._newDevice(deviceJson)
                if not device:
                    _LOGGER.info("Device is unknown")
                    continue
                self._devices[device.device_id] = device
