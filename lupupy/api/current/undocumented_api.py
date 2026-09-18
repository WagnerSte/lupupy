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

ACTION_RECORD_LIST_GET = "recordListGet"

TOKEN_LIFETIME = 60




@undocumented(
    "the REST actions of the XT1 Plus and later beyond the manufacturer's "
    "document, worked out by watching the panel and its web interface"
)
class UndocumentedApi(VendorApi):
    """One method per REST action the panel answers beyond the document."""

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
