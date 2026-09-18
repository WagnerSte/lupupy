"""Facade over the REST actions the manufacturer does not specify.

The XT1 Plus and its successors answer far more than the six actions in
the manufacturer's document. Everything here was worked out by watching the
panel and its web interface, whose /js/script.js names every action it
uses. Each method is marked with @undocumented and says where the knowledge
came from: it works on the panels it was tried against, and a firmware
update is free to change it.

As in lupupy.api.current.vendor_api, each public method stands for exactly one
action, is named after it in snake_case, and returns the panel's answer as
it comes. The first XT1 speaks a different API altogether, which lives in
lupupy.api.legacy.undocumented_legacy_api.
"""

import time

from lupupy.api.current.vendor_api import VendorApi
from lupupy.api.markers import undocumented

ACTION_WELCOME_GET = "welcomeGet"
ACTION_DEVICE_GET = "deviceGet"
ACTION_AREA_LIST_GET = "areaListGet"
ACTION_RECORD_LIST_GET = "recordListGet"

TOKEN_LIFETIME = 60




@undocumented(
    "the REST actions of the XT1 Plus and later beyond the manufacturer's "
    "document, worked out by watching the panel and its web interface"
)
class UndocumentedApi(VendorApi):
    """One method per REST action the panel answers beyond the document."""

    @undocumented("welcomeGet, which the web interface asks first when it loads")
    def welcome_get(self) -> dict:
        """GET welcomeGet, the firmware and hardware of the panel.

        Returns:
            {"updates": {"version": "HPGW-G1 0.0.3.7J HPGW-L2-XA35H",
            "em_ver", "rf_ver", "rf_ext_cap", "rf_ext_ver", "zb_ver",
            "zbs_ver", "zw_ver", "gsm_ver", "publicip", "ip", "mac"}}. The
            first word of version names the hardware, the second the
            firmware. The *_ver fields are empty for modules the panel does
            not have.
        """
        return self._get(ACTION_WELCOME_GET)

    @undocumented("deviceGet, which the web interface reads its device view from")
    def device_get(self) -> dict:
        """GET deviceGet, every device with the details the interface shows.

        Returns:
            {"senrows": [<device>, ...]}, with the fields of deviceListGet
            and more: onOff and level for switches and shutters, and for
            Zigbee devices profile, device, cluster, manu and serial, which
            lupupy.api.current.capabilities looks kinds of device up by.
        """
        return self._get(ACTION_DEVICE_GET)

    @undocumented("areaListGet, which the web interface fills its area picker from")
    def area_list_get(self) -> dict:
        """GET areaListGet, the names of the areas.

        Returns:
            {"arearows": {"1": "1 Haus", "2": "2 Keller"}}. The panel puts
            the area number in front of each name for display; the name as
            configured is "Haus".
        """
        return self._get(ACTION_AREA_LIST_GET)

    @undocumented("recordListGet, the event log")
    def record_list_get(self) -> dict:
        """GET recordListGet, the most recent entries of the event log.

        Returns:
            {"logrows": [<row>, ...]}, newest first, a row carrying uid,
            time (epoch seconds as a string), area, zone, sid, name, type,
            type_f such as "{D_TYPE_9}", user and event such as
            "{ALARM_HISTORY_183}\\t1". The panel keeps a limited number.
        """
        return self._get(ACTION_RECORD_LIST_GET)

    @undocumented(
        "the panel refuses a token older than a minute, which the document "
        "does not mention"
    )
    def _ensure_token(self) -> None:
        if time.time() - self._token_time > TOKEN_LIFETIME:
            self._token = None
        super()._ensure_token()
