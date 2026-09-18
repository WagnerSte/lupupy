"""Tests for the devices the panel reports."""

from unittest.mock import MagicMock

import lupupy.constants as CONST
from lupupy.devices import LupusecDevice
from lupupy.devices.binary_sensor import LupusecBinarySensor
from lupupy.devices.switch import LupusecSwitch
from lupupy.lupusec import Lupusec


def make_payload(**overrides) -> dict:
    """Build a device payload as the panel's device list reports it."""
    payload = {
        "device_id": "ZS:00000001",
        "name": "Smoke Detector",
        "type": CONST.TYPE_SMOKE_XT,
        "status": CONST.STATUS_CLOSED,
        "battery_ok": "1",
        "tamper_ok": "1",
        "cond_ok": "1",
        "bypass": 0,
        "rssi": "{WEB_MSG_STRONG}\t9",
        "area": "1",
        "zone": "3",
    }
    payload.update(overrides)
    return payload


def make_device(**overrides) -> LupusecDevice:
    return LupusecDevice(make_payload(**overrides))


def test_the_ok_fields_are_inverted() -> None:
    """The panel reports '1' while a device is healthy.

    All three were read from a 'faults' object no panel ever sends, so
    reading any of them raised AttributeError.
    """
    healthy = make_device()
    faulty = make_device(battery_ok="0", tamper_ok="0", cond_ok="0")

    assert (healthy.battery_low, healthy.tampered, healthy.out_of_order) == (
        False,
        False,
        False,
    )
    assert (faulty.battery_low, faulty.tampered, faulty.out_of_order) == (
        True,
        True,
        True,
    )


def test_fields_the_panel_leaves_out() -> None:
    """The alarm panel reports no signal strength and no battery.

    A device that reports no signal strength is not therefore unreachable.
    """
    device = make_device()
    del device._json_state["battery_ok"]
    del device._json_state["rssi"]

    assert device.battery_low is False
    assert device.rssi is None
    assert device.no_response is False


def test_bypass_and_signal_strength() -> None:
    """The signal arrives behind a placeholder, or not at all.

    A sender the panel cannot measure reports N/A, and the panel's own
    field holds the interference it sees as a bare number. Neither is a
    device that stopped answering.
    """
    assert make_device(bypass=1).bypassed is True
    assert make_device(bypass=0).bypassed is False

    measured = {
        raw: (device.rssi, device.no_response)
        for raw in ("{WEB_MSG_STRONG}\t9", "{WEB_MSG_WEAK}\t0", "{WEB_MSG_NA}", "5")
        for device in [make_device(rssi=raw)]
    }

    assert measured == {
        "{WEB_MSG_STRONG}\t9": (9, False),
        "{WEB_MSG_WEAK}\t0": (0, True),
        "{WEB_MSG_NA}": (None, False),
        "5": (None, False),
    }


def test_the_device_factory() -> None:
    """Motion detectors and senders were dropped as unknown.

    A Sonos speaker the panel only passes through still is.
    """
    system = object.__new__(Lupusec)
    built = {
        type_tag: type(system._newDevice(make_payload(type=type_tag)))
        for type_tag in (
            CONST.TYPE_CONTACT_XT,
            CONST.TYPE_MOTION_XT,
            CONST.TYPE_POWER_SWITCH_1_XT,
            CONST.TYPE_REMOTE_XT,
            CONST.TYPE_STATUS_DISPLAY_XT,
            CONST.TYPE_SMART_SWITCH_XT,
            107,
        )
    }

    assert built == {
        CONST.TYPE_CONTACT_XT: LupusecBinarySensor,
        CONST.TYPE_MOTION_XT: LupusecBinarySensor,
        CONST.TYPE_POWER_SWITCH_1_XT: LupusecSwitch,
        CONST.TYPE_REMOTE_XT: LupusecDevice,
        CONST.TYPE_STATUS_DISPLAY_XT: LupusecDevice,
        CONST.TYPE_SMART_SWITCH_XT: LupusecDevice,
        107: type(None),
    }


def test_an_unnamed_device_is_named_after_its_type() -> None:
    """Sockets, shutters and senders had no entry in the translation."""
    named = {
        type_tag: make_device(type=type_tag, name="", device_id="RF:2").name
        for type_tag in (
            CONST.TYPE_MOTION_XT,
            CONST.TYPE_POWER_SWITCH_2_XT,
            CONST.TYPE_SMART_SWITCH_XT,
        )
    }

    assert named == {
        CONST.TYPE_MOTION_XT: "motion RF:2",
        CONST.TYPE_POWER_SWITCH_2_XT: "Funksteckdose V2 RF:2",
        CONST.TYPE_SMART_SWITCH_XT: "Smart Switch RF:2",
    }


def test_refresh_reads_the_endpoint_the_device_belongs_to() -> None:
    """Everything outside the opening contacts fell through every branch."""
    api = MagicMock()
    api.get_sensors.return_value = [make_payload(status="Offen")]
    api.get_power_switches.return_value = [
        make_payload(type=CONST.TYPE_POWER_SWITCH, status="on")
    ]
    api.get_panel.return_value = make_payload(type=CONST.ALARM_TYPE, status="Armed")

    sensor = make_device()
    socket = make_device(type=CONST.TYPE_POWER_SWITCH)
    alarm = make_device(type=CONST.ALARM_TYPE)
    for device in (sensor, socket, alarm):
        device.refresh(api)

    assert (sensor.status, socket.status, alarm.status) == ("Offen", "on", "Armed")


def test_refresh_keeps_every_field_fresh() -> None:
    """Only fields that already held a value were merged, and only status.

    A device the panel no longer reports leaves the loop empty, which used
    to return the last entry of the list or raise UnboundLocalError.
    """
    api = MagicMock()
    device = make_device(type=CONST.TYPE_CONTACT_XT)
    api.get_sensors.return_value = [
        make_payload(type=CONST.TYPE_CONTACT_XT, battery_ok="0")
    ]

    device.refresh(api)
    assert device.battery_low is True

    api.get_sensors.return_value = []
    assert device.refresh(api) is None


def test_a_device_survives_a_refresh() -> None:
    """Devices are kept under their id but were looked up by name.

    The lookup therefore never matched and every refresh replaced every
    device with a new object, so a caller holding one saw it go stale.
    """
    system = object.__new__(Lupusec)
    system._devices = {}
    system.api = MagicMock()
    system.api.get_sensors.return_value = [make_payload()]

    system._update_devices()
    first = system._devices["ZS:00000001"]

    system.api.get_sensors.return_value = [make_payload(status="Offen")]
    system._update_devices()

    assert system._devices["ZS:00000001"] is first
    assert first.status == "Offen"


def test_the_alarm_panel_knows_what_it_is() -> None:
    """Its type was missing from the translation."""
    assert make_device(type=CONST.ALARM_TYPE).generic_type == "Alarmanlage"
