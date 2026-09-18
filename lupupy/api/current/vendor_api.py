"""Facade over the part of the panel's web API the manufacturer specifies.

Everything in this module comes from "LUPUSEC API", the LUPUSEC XT API
document, version 1.0.0, which Lupus Electronics supplies on request. The
copy this was written from was obtained on 2026-09-17; the file itself was
written in February 2017 and last revised in June 2020.

Each public method of VendorApi stands for exactly one REST action and is
named after it in snake_case, so panelCondGet is panel_cond_get(). It sends
the parameters the document lists and returns the panel's answer as it
comes, parsed from JSON but otherwise untouched. Where the panel behaves
differently from the document, the docstring says so, and working around it
is left to the caller: lupupy.api.current.helper does that.

That the document is older than the firmware it describes is the point of
keeping it separate: these actions are what the manufacturer committed to,
so they are the ones worth relying on, while anything beyond them may be
gone after an update. Those others live in lupupy.api.current.undocumented_api,
and the API of the first XT1 in lupupy.api.legacy.undocumented_legacy_api.
"""

import logging
import time
from typing import Any

from lupupy.api.transport import REQUEST_TIMEOUT, Transport
from lupupy.exceptions import LupusecException

_LOGGER = logging.getLogger(__name__)

ACTION_TOKEN_GET = "tokenGet"
ACTION_DEVICE_LIST_GET = "deviceListGet"
ACTION_DEVICE_LIST_PSS_GET = "deviceListPSSGet"
ACTION_DEVICE_SWITCH_PSS_POST = "deviceSwitchPSSPost"
ACTION_PANEL_COND_GET = "panelCondGet"
ACTION_PANEL_COND_POST = "panelCondPost"

# deviceSwitchPSSPost, form parameter "switch".
SWITCH_OFF = 0
SWITCH_ON = 1
SWITCH_STOP = 2
SHUTTER_DOWN = SWITCH_OFF
SHUTTER_UP = SWITCH_ON
SHUTTER_STOP = SWITCH_STOP

# panelCondPost, form parameter "mode". The panel keeps three home modes,
# which it arms separately.
MODE_DISARM = 0
MODE_ARM = 1
MODE_HOME1 = 2
MODE_HOME2 = 3
MODE_HOME3 = 4

# panelCondPost, form parameter "area".
AREAS = (1, 2)



class VendorApi(Transport):
    """One method per REST action the manufacturer specifies."""

    def token_get(self) -> dict:
        """GET tokenGet. Every write request has to carry the token.

        Returns:
            {"result": 1, "message": <token>}. The token goes into the
            X-Token header of later requests.

        The document does not say so, but the panel answers the first
        request of a new session with an error page instead of JSON. That
        rejected request is what establishes the session, so asking again
        is expected; this method raises LupusecException for it.
        """
        response = self.session.get(
            self.api_url + ACTION_TOKEN_GET, timeout=REQUEST_TIMEOUT
        )
        return self._decode(ACTION_TOKEN_GET, response.text)

    def device_list_get(self) -> dict:
        """GET deviceListGet, every sensor the panel has learned.

        Returns:
            {"senrows": [<sensor>, ...]}, a sensor being a dict with, among
            others, area, zone, type, type_f, name, sid, status, status_ex,
            cond, cond_ok, battery, battery_ok, tamper, tamper_ok, bypass,
            rssi, su, ver, ammeter, alarm_status and resp_mode.

        The *_ok fields read "1" while all is well and "0" on a fault.
        """
        return self._get(ACTION_DEVICE_LIST_GET)

    def device_list_pss_get(self) -> dict:
        """GET deviceListPSSGet, every switch, relay and shutter relay.

        Returns:
            {"pssrows": [<switch>, ...]}, a switch being a dict with area,
            zone, id, name, type, type_f, status, level, ammeter and
            consumer_id.

        level is the dimmer value of a switch or the position of a shutter.
        For a shutter it is the panel's own reckoning from the running time
        and only changes once the shutter stands still; -1 when the panel
        does not know it.
        """
        return self._get(ACTION_DEVICE_LIST_PSS_GET)

    def device_switch_pss_post(
        self,
        id: str,  # noqa: A002
        switch: int | None = None,
        level: int | None = None,
        pd: int | str | None = None,
    ) -> dict:
        """POST deviceSwitchPSSPost, switch a socket, relay or shutter.

        Args:
            id: the device id from deviceListPSSGet, such as "ZS:64a701".
            switch: SWITCH_OFF, SWITCH_ON or SWITCH_STOP, which a shutter
                reads as down, up and stop.
            level: a dimmer value or a shutter position.
            pd: the minutes after which the panel switches off again.

        Returns:
            {"result": 1 on success else 0, "message": <text>}.

        Parameters left as None are not sent. The document calls all but id
        optional, but the panel differs:

        - Without switch the call is refused with
          {WEB_ERR_PARAM_RANGE} switch 0 2.
        - Without pd a socket answers result 1 and does not switch. Sent
          empty, pd means "until switched again".
        - level does not move a shutter of Zigbee type 512 ("Shade"); it is
          accepted and the shutter runs to the end of its travel. The web
          interface sends positions to devices that take them through
          deviceSwitchDimmerPost instead.

        Observed on an XT1 Plus: switch and level with a type 512 shutter on
        2026-09-17, pd with a type 9 socket on 2026-09-18. Not verified on
        other models or firmware versions.
        """
        params: dict[str, Any] = {"id": id}
        for name, value in (("switch", switch), ("level", level), ("pd", pd)):
            if value is not None:
                params[name] = value
        return self._post(ACTION_DEVICE_SWITCH_PSS_POST, params)

    def panel_cond_get(self) -> dict:
        """GET panelCondGet, the state of the panel itself.

        Returns:
            {"updates": {...}, "forms": {"pcondform1": {"mode", "f_arm"},
            "pcondform2": {...}}}. The updates carry mode_a1 and mode_a2 as
            placeholders such as "{AREA_MODE_2}", and the panel's own
            condition: battery_ok, tamper_ok, interference_ok,
            ac_activation_ok and sig_gsm_ok, each "1" while all is well, and
            dc_ex, "0" while at least one contact is open. rssi is the radio
            interference the panel sees, 1 to 9, not a signal it receives.
        """
        return self._get(ACTION_PANEL_COND_GET)

    def panel_cond_post(self, area: int, mode: int) -> dict:
        """POST panelCondPost, arm or disarm one area.

        Args:
            area: 1 or 2.
            mode: MODE_DISARM, MODE_ARM, MODE_HOME1, MODE_HOME2 or
                MODE_HOME3.

        Returns:
            {"result": 1 on success else 0, "message": <text>}.
        """
        return self._post(ACTION_PANEL_COND_POST, {"area": area, "mode": mode})

    def _uses_token(self) -> bool:
        """Every request of the XT and its successors carries a token."""
        return True

    def _ensure_token(self) -> None:
        """Fetch a token if there is none yet."""
        if self._uses_token() and self._token is None:
            self._token = self._fetch_token()
            self._token_time = time.time()

    def _fetch_token(self) -> str:
        """Ask for a token twice, as a new session needs."""
        for attempt in range(2):
            try:
                return self.token_get()["message"]
            except (LupusecException, KeyError):
                _LOGGER.debug(
                    "Token request %s did not return a token, the session was "
                    "most likely not established yet",
                    attempt + 1,
                )
        raise LupusecException("Unable to get a token from the panel")
