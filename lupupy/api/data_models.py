"""Data models for the Lupusec API."""

from enum import Enum

import lupupy.constants as CONST


class LupusecModelType(Enum):
    """Model type."""

    XT1 = 1
    XT2_3_4 = 2


class LupusecAlarmMode(Enum):
    """Enum for alarm mode."""

    Unknown = CONST.MODE_UNKNOWN
    Armed = CONST.MODE_ARMED
    Disarmed = CONST.MODE_DISARMED
    Home = CONST.MODE_HOME
    AlarmTriggered = CONST.STATE_ALARM_TRIGGERED
