"""Lupusec cover device."""

from typing import TYPE_CHECKING

from lupupy.api.current.vendor_api import SHUTTER_DOWN, SHUTTER_STOP, SHUTTER_UP
from lupupy.devices import LupusecDevice

if TYPE_CHECKING:
    from lupupy.api.current.helper import LupusecApi


class LupusecCover(LupusecDevice):
    """Class to represent a roller shutter.

    Whether a shutter can be sent to a position depends on its actuator.
    The common Zigbee type 512 ("Shade") only goes up and down: a level
    sent to it is accepted and ignored, and it runs to the end of its
    travel either way. Leaving it part way open means giving a direction
    and a stop after the right share of its travel time, which differs from
    one installation to the next. That lands near the wanted
    height rather than on it, because the shutter keeps running while the
    stop is on its way.

    The panel reports a position only for a shutter standing still, and
    only after a delay: during a travel, and for some time after it, it
    answers with the position the shutter last came to rest at. The value
    is the panel's own reckoning from the running time, not a measurement,
    so between the ends it can differ noticeably from where the shutter
    actually stands. Only the ends of the travel are worth trusting.

    Observed on an XT1 Plus with a type 512 shutter on 2026-09-17 and not
    yet verified on other models, actuators or firmware versions.
    """

    def open_cover(self, api: "LupusecApi") -> bool:
        """Move the shutter up."""
        return api.move_shutter(self.device_id, SHUTTER_UP)

    def close_cover(self, api: "LupusecApi") -> bool:
        """Move the shutter down."""
        return api.move_shutter(self.device_id, SHUTTER_DOWN)

    def stop_cover(self, api: "LupusecApi") -> bool:
        """Stop a moving shutter."""
        return api.move_shutter(self.device_id, SHUTTER_STOP)
