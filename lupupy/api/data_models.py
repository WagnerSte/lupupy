"""Data models for the Lupusec API."""

from dataclasses import dataclass
from enum import Enum

import lupupy.constants as CONST


class LupusecModelType(Enum):
    """The generation of the panel's web API.

    The first XT1 speaks an API of its own; the XT1 Plus, XT2, XT3 and XT4
    share the one the manufacturer documents. LupusecModel.generation says
    which a panel belongs to.
    """

    XT1_Legacy = 1
    XT1Plus_2_3_4 = 2


class LupusecModel(Enum):
    """The panel as it says on the device.

    The user states it when configuring the library; the library does not
    guess it. Each belongs to one generation of the panel's web API.
    """

    XT1 = "XT1"
    XT1_PLUS = "XT1 Plus"
    XT2 = "XT2"
    XT2_PLUS = "XT2 Plus"
    XT3 = "XT3"
    XT4 = "XT4"

    @property
    def generation(self) -> LupusecModelType:
        """The web API this panel speaks."""
        if self is LupusecModel.XT1:
            return LupusecModelType.XT1_Legacy
        return LupusecModelType.XT1Plus_2_3_4


class LupusecAlarmMode(Enum):
    """Enum for alarm mode."""

    Unknown = CONST.MODE_UNKNOWN
    Armed = CONST.MODE_ARMED
    Disarmed = CONST.MODE_DISARMED
    Home = CONST.MODE_HOME
    Home2 = CONST.MODE_HOME2
    Home3 = CONST.MODE_HOME3
    AlarmTriggered = CONST.STATE_ALARM_TRIGGERED


@dataclass(frozen=True)
class PanelInfo:
    """What runs on the panel, as welcomeGet reports it."""

    firmware: str
    version: str
    radio: str
    zigbee: str
    gsm: str
    mac: str
