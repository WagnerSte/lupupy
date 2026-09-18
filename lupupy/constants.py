"""Constants for the Lupusec alarm panel."""

# Used in setup.py
VERSION = "0.3.3-dev-1"
PROJECT_PACKAGE_NAME = "lupupy"
PROJECT_LICENSE = "MIT"
PROJECT_URL = "http://www.github.com/majuss/lupupy"
PROJECT_DESCRIPTION = "A python cli for Lupusec alarm panels."
PROJECT_LONG_DESCRIPTION = (
    "lupupy is a python3 interface for"
    " the Lupus Electronics alarm panel."
    " Its intented to get used in various"
    " smart home services to get a full"
    " integration of all your devices."
)
PROJECT_AUTHOR = "Majuss"

MODE_UNKNOWN = "Unknown"
MODE_ARMED = "Arm"
MODE_HOME = "Home"
MODE_DISARMED = "Disarm"
MODE_ALARM_TRIGGERED = "Einbruch"
MODE_ALARM_TRIGGERED_XT2 = "3"
ALL_MODES = [MODE_DISARMED, MODE_HOME, MODE_ARMED]

XT2_MODES_TO_TEXT = {
    "{AREA_MODE_0}": "Disarm",
    "{AREA_MODE_1}": "Arm",
    "{AREA_MODE_2}": "Home",
    "{AREA_MODE_3}": "Home",
    "{AREA_MODE_4}": "Home",
}

STATE_ALARM_DISARMED = "disarmed"
STATE_ALARM_ARMED_HOME = "armed_home"
STATE_ALARM_ARMED_AWAY = "armed_away"
STATE_ALARM_TRIGGERED = "alarm_triggered"
MODE_TRANSLATION_GENERIC = {
    "Disarm": "disarmed",
    "Home": "armed_home",
    "Arm": "armed_away",
}
DEFAULT_MODE = MODE_ARMED

HISTORY_REQUEST_XT1 = "historyGet"
HISTORY_REQUEST_XT2 = "recordListGet"
HISTORY_ALARM_COLUMN = "a"
HISTORY_ALARM_COLUMN_XT2 = "type"
HISTORY_HEADER = "hisrows"
HISTORY_HEADER_XT2 = "logrows"
HISTORY_CACHE_NAME = ".lupusec_history_cache"

STATUS_ON_INT = 0
STATUS_ON = "on"
STATUS_OFF_INT = 1
STATUS_OFF = "off"
STATUS_OFFLINE = "offline"
STATUS_CLOSED = "Geschlossen"
STATUS_CLOSED_INT = 0
STATUS_OPEN = "Offen"
STATUS_OPEN_INT = 1
STATUS_OPEN_WEB = "{WEB_MSG_DC_OPEN}"
STATUS_CLOSED_WEB = "{WEB_MSG_DC_CLOSE}"


ALARM_NAME = "Lupusec Alarm"
ALARM_DEVICE_ID = "0"
ALARM_TYPE = "Alarm"

# GENERIC Lupusec DEVICE TYPES
TYPE_WINDOW = "Fensterkontakt"
TYPE_DOOR = "Türkontakt"
TYPE_SMOKE = "Rauchmelder"
TYPE_WATER = "Wassermelder"
TYPE_POWER_SWITCH = "Steckdose"
TYPE_REMOTE_XT = 2
TYPE_CONTACT_XT = 4
TYPE_MOTION_XT = 9
TYPE_STATUS_DISPLAY_XT = 22
TYPE_SMART_SWITCH_XT = 81
TYPE_WATER_XT = 5
TYPE_SMOKE_XT = 11
TYPE_POWER_SWITCH_1_XT = 24
TYPE_POWER_SWITCH_2_XT = 25
TYPE_KEYPAD_V2 = 37
TYPE_INDOOR_SIREN_XT = 45
TYPE_OUTDOOR_SIREN_XT = 46
TYPE_SHUTTER_XT = 76
TYPE_SWITCH = [TYPE_POWER_SWITCH, TYPE_POWER_SWITCH_1_XT, TYPE_POWER_SWITCH_2_XT]
TYPE_OPENING = [TYPE_DOOR, TYPE_WINDOW, TYPE_CONTACT_XT]
TYPE_SIREN = [TYPE_INDOOR_SIREN_XT, TYPE_OUTDOOR_SIREN_XT]
TYPE_KEYPAD = [TYPE_KEYPAD_V2]
TYPE_COVER = [TYPE_SHUTTER_XT]
TYPE_MOTION = [TYPE_MOTION_XT]

# Senders and indicators. They report no state of their own, only how
# they are doing, and announce what they did through the event log.
TYPE_ACCESSORY = [TYPE_REMOTE_XT, TYPE_STATUS_DISPLAY_XT, TYPE_SMART_SWITCH_XT]
BINARY_SENSOR_TYPES = TYPE_OPENING
TYPE_SENSOR = [TYPE_SMOKE, TYPE_WATER, TYPE_WATER_XT, TYPE_SMOKE_XT]


# Home Assistant DEVICE TYPES
HA_DEVICE_CLASS_WINDOW = "window"
HA_DEVICE_CLASS_DOOR = "door"
HA_DEVICE_CLASS_MOISTURE = "moisture"
HA_DEVICE_CLASS_SMOKE = "smoke"
HA_DEVICE_CLASS_MOTION = "motion"

TYPE_TRANSLATION = {
    TYPE_WINDOW: HA_DEVICE_CLASS_WINDOW,
    TYPE_DOOR: HA_DEVICE_CLASS_DOOR,
    TYPE_CONTACT_XT: HA_DEVICE_CLASS_DOOR,
    TYPE_WATER_XT: HA_DEVICE_CLASS_MOISTURE,
    TYPE_SMOKE_XT: HA_DEVICE_CLASS_SMOKE,
    TYPE_MOTION_XT: HA_DEVICE_CLASS_MOTION,
    TYPE_REMOTE_XT: "Fernbedienung",
    TYPE_STATUS_DISPLAY_XT: "Statusanzeige",
    TYPE_SMART_SWITCH_XT: "Smart Switch",
    ALARM_TYPE: "Alarmanlage",
    TYPE_KEYPAD_V2: "Keypad V2",
    TYPE_INDOOR_SIREN_XT: "Innensirene",
    TYPE_OUTDOOR_SIREN_XT: "Außensirene",
    TYPE_SHUTTER_XT: "Rolladen",
    TYPE_POWER_SWITCH: "Steckdose",
    TYPE_POWER_SWITCH_1_XT: "Funksteckdose",
    TYPE_POWER_SWITCH_2_XT: "Funksteckdose V2",
}
DEVICES_API_XT1 = "sensorListGet"
DEVICES_API_XT2 = "deviceListGet"
