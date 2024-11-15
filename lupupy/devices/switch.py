"""Lupusec switch device."""

import lupupy.constants as CONST
from lupupy.devices import LupusecDevice


class LupusecSwitch(LupusecDevice):
    """Class to add switch functionality."""

    def switch_on(self) -> bool:
        """Turn the switch on."""
        success = self.set_status(CONST.STATUS_ON_INT)

        if success:
            self._json_state["status"] = CONST.STATUS_ON

        return success

    def switch_off(self) -> bool:
        """Turn the switch off."""
        success = self.set_status(CONST.STATUS_OFF_INT)

        if success:
            self._json_state["status"] = CONST.STATUS_OFF

        return success

    @property
    def is_on(self) -> bool:
        """Get switch state.

        Assume switch is on.
        """
        return self.status not in (CONST.STATUS_OFF, CONST.STATUS_OFFLINE)

    @property
    def is_dimmable(self) -> bool:
        """Device dimmable."""
        return False
