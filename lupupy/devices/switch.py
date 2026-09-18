"""Lupusec switch device."""

from typing import TYPE_CHECKING

import lupupy.constants as CONST
from lupupy.devices import LupusecDevice

if TYPE_CHECKING:
    from lupupy.api.current.helper import LupusecApi


class LupusecSwitch(LupusecDevice):
    """Class to add switch functionality."""

    def switch_on(self, api: "LupusecApi") -> bool:
        """Turn the switch on."""
        success = self.set_status(True, api)

        if success:
            self._json_state["status"] = CONST.STATUS_ON

        return success

    def switch_off(self, api: "LupusecApi") -> bool:
        """Turn the switch off."""
        success = self.set_status(False, api)

        if success:
            self._json_state["status"] = CONST.STATUS_OFF

        return success

    @property
    def is_on(self) -> bool:
        """Get switch state.

        Assume switch is on.
        """
        return self.status not in (CONST.STATUS_OFF, CONST.STATUS_OFFLINE)
