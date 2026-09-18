"""Facade over the REST actions of the first XT1.

The first XT1 predates the manufacturer's API document and speaks an API of
its own: no token, answers that are not JSON, other action names and other
values. Nothing here is documented; it all comes from earlier versions of
this library, and none of it was verified in this version, for want of a
first XT1 to try it on.

As in the other facades, each public method stands for exactly one action,
is named after it in snake_case, and returns the panel's answer as it comes.
The XT1 Plus and its successors are reached through
lupupy.api.current.undocumented_api instead.
"""

import yaml

from lupupy.api.transport import Transport
from lupupy.api.markers import undocumented

ACTION_SENSOR_LIST_GET = "sensorListGet"
ACTION_PSS_STATUS_GET = "pssStatusGet"
ACTION_HISTORY_GET = "historyGet"
ACTION_PANEL_COND_GET = "panelCondGet"
ACTION_PANEL_COND_POST = "panelCondPost"
ACTION_LOGIN = "login"

# panelCondPost, form parameter "mode", on the first XT1.
MODE_ARM = 0
MODE_HOME = 1
MODE_DISARM = 2


@undocumented(
    "the API of the first XT1, which predates the manufacturer's document; "
    "taken from earlier versions of this library and not verified here"
)
class UndocumentedLegacyApi(Transport):
    """One method per REST action of the first XT1."""

    @undocumented("login, which the first XT1 expects before anything else")
    def login_post(self) -> dict:
        """POST login.

        Returns:
            What the panel answers, which the library does not use.
        """
        return self._post(ACTION_LOGIN)

    @undocumented("sensorListGet, the sensor list of the first XT1")
    def sensor_list_get(self) -> dict:
        """GET sensorListGet, the sensors.

        Returns:
            {"senrows": [<sensor>, ...]}, a sensor carrying no as its id and
            cond as its state.
        """
        return self._get(ACTION_SENSOR_LIST_GET)

    @undocumented("pssStatusGet, the power switches of the first XT1")
    def pss_status_get(self) -> dict:
        """GET pssStatusGet, the power switches.

        Returns:
            {"forms": {<form>: {"ready", "pssonoff", "name"}, ...}}, one form
            per switch slot, ready 1 when a switch is set up in it.
        """
        return self._get(ACTION_PSS_STATUS_GET)

    @undocumented("historyGet, the event log of the first XT1")
    def history_get(self) -> dict:
        """GET historyGet, the event log.

        Returns:
            {"hisrows": [<row>, ...]}, a row carrying the event text in a.
        """
        return self._get(ACTION_HISTORY_GET)

    @undocumented("panelCondGet on the first XT1, which reports its mode as text")
    def panel_cond_get(self) -> dict:
        """GET panelCondGet, the state of the panel.

        Returns:
            {"updates": {...}}, with the mode in mode_st as text such as
            "Disarm".
        """
        return self._get(ACTION_PANEL_COND_GET)

    @undocumented(
        "panelCondPost on the first XT1, which knows a single area and "
        "numbers its modes differently"
    )
    def panel_cond_post(self, mode: int) -> dict:
        """POST panelCondPost, arm or disarm the panel.

        Args:
            mode: MODE_ARM, MODE_HOME or MODE_DISARM of this module.

        Returns:
            {"result": 1 on success else 0, ...}.
        """
        return self._post(ACTION_PANEL_COND_POST, {"mode": mode})

    @undocumented(
        "the first XT1 answers with a first line to skip and YAML after it "
        "rather than JSON"
    )
    def _decode(self, action: str, text: str) -> dict:
        text = text.replace("\t", "")
        return yaml.load(text[text.index("\n") + 1 : -2], Loader=yaml.BaseLoader)
