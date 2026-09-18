"""Tests for the REST facade and the helpers built on it."""

import json
import time
from unittest.mock import MagicMock, call

import pytest

from lupupy.api.current import vendor_api
from lupupy.api.data_models import LupusecAlarmMode, LupusecModel, LupusecModelType
import lupupy.api as api_package
from lupupy.api.current import helper as current_helper
from lupupy.api.legacy import undocumented_legacy_api
from lupupy.api.legacy.undocumented_legacy_api import UndocumentedLegacyApi
from lupupy.api.current.helper import LupusecApi
from lupupy.api.legacy.helper import LegacyLupusecApi
from lupupy.api.current.undocumented_api import UndocumentedApi
from lupupy.exceptions import LupusecException, LupusecNotSupportedException

TOKEN_RESPONSE = '{"result": 1, "message": "abc123"}'
OK = '{"result": 1, "message": "{WEB_MSG_SUBMIT_SUCCESS}"}'

# Shaped like recordListGet, raw tabs included.
RECORD_LIST = """{
  "logrows": [
{"uid": 8858, "time": "1789511715", "area": "1", "zone": "2", "sid": "RF:00000001", "name": "Hallway ", "type_f": "{D_TYPE_9}", "type": "1", "user": "", "event": "{ALARM_HISTORY_183}\t1", "mark_read": 0 },
{"uid": 8857, "time": "1789443000", "area": "1", "zone": "", "sid": "", "name": "", "type_f": "", "type": "2", "user": "{WEB_MSG_USER_ID}\t1(user)", "event": "{ALARM_HISTORY_57}\t1", "mark_read": 1 },
{"uid": 8856, "time": "1789423363", "area": "1", "zone": "41", "sid": "RF:00000002", "name": "Keypad", "type_f": "{D_TYPE_37}", "type": "2", "user": "", "event": "{ALARM_HISTORY_81}\t1", "mark_read": 1 }
  ]
}"""


def answer(text: str, status_code: int = 200) -> MagicMock:
    return MagicMock(text=text, status_code=status_code)


def make_rest(cls: type = UndocumentedApi) -> UndocumentedApi:
    """A facade whose HTTP session is a mock, holding a fresh token."""
    rest = object.__new__(cls)
    rest.base_url = "http://panel.lan"
    rest.api_url = "http://panel.lan/action/"
    rest._token = "current"
    rest._token_time = time.time()
    rest.session = MagicMock()
    rest.session.get.return_value = answer(OK)
    rest.session.post.return_value = answer(OK)
    return rest


def make_api(legacy: bool = False) -> LupusecApi:
    """Helpers over a facade that is a mock altogether."""
    api = object.__new__(LegacyLupusecApi if legacy else LupusecApi)
    api.rest = MagicMock()
    api.rest.device_switch_pss_post.return_value = json.loads(OK)
    api.rest.panel_cond_post.return_value = json.loads(OK)
    api.rest.record_list_get.return_value = json.loads(RECORD_LIST.replace("\t", ""))
    api._cache = {}
    api._history_cache = []
    return api


def test_getting_a_token() -> None:
    """The panel rejects the first request of a session with an error page.

    That rejected request is what establishes the session, so asking twice
    is expected. A panel that never answers with a token is not.
    """
    rest = make_rest()
    rest.session.get.side_effect = [
        answer("Zugriff verweigert: Sitzung abgelaufen!"),
        answer(TOKEN_RESPONSE),
    ]

    assert rest._fetch_token() == "abc123"
    assert rest.session.get.call_count == 2

    rest.session.get.side_effect = None
    rest.session.get.return_value = answer("Zugriff verweigert!")
    with pytest.raises(LupusecException):
        rest._fetch_token()


def test_the_token_is_renewed_once_it_expires() -> None:
    """Only the XT and its successors work with a token at all."""
    renewed = {}
    for name, cls, age in (
        ("fresh", UndocumentedApi, 0),
        ("expired", UndocumentedApi, 61),
        ("xt1", UndocumentedLegacyApi, 3600),
    ):
        rest = make_rest(cls)
        rest._token = None if cls is UndocumentedLegacyApi else "current"
        rest._token_time = time.time() - age
        rest.session.get.return_value = answer(TOKEN_RESPONSE)
        rest._ensure_token()
        renewed[name] = rest._token

    assert renewed == {"fresh": "current", "expired": "abc123", "xt1": None}


def test_a_rejected_request_is_sent_again_with_a_fresh_token() -> None:
    """Tokens run out; a second rejection is an error that says why."""
    rest = make_rest()
    rest.session.get.side_effect = [
        answer("", 401),
        answer(TOKEN_RESPONSE),
        answer('{"updates": {}}'),
    ]

    assert rest.panel_cond_get() == {"updates": {}}

    rest.session.get.side_effect = None
    rest.session.get.return_value = answer(TOKEN_RESPONSE, 401)
    with pytest.raises(LupusecException) as excinfo:
        rest.panel_cond_get()
    assert "401" in str(excinfo.value)


def test_the_facade_sends_what_it_is_given_and_returns_what_comes() -> None:
    """One REST action per method, the answer untouched.

    Parameters left as None are not sent, as the document calls them
    optional; working around the panel is the helpers' job.
    """
    rest = make_rest()

    result = rest.device_switch_pss_post("ZS:01", switch=vendor_api.SWITCH_ON)
    rest.panel_cond_post(2, vendor_api.MODE_HOME2)

    assert result == json.loads(OK)
    assert rest.session.post.call_args_list == [
        call(
            "http://panel.lan/action/deviceSwitchPSSPost",
            data={"id": "ZS:01", "switch": vendor_api.SWITCH_ON},
            headers={"X-Token": "current"},
            timeout=vendor_api.REQUEST_TIMEOUT,
        ),
        call(
            "http://panel.lan/action/panelCondPost",
            data={"area": 2, "mode": vendor_api.MODE_HOME2},
            headers={"X-Token": "current"},
            timeout=vendor_api.REQUEST_TIMEOUT,
        ),
    ]

    rest.session.get.return_value = answer('{"senrows": []}')
    assert rest.device_list_get() == {"senrows": []}


def test_arming_the_panel() -> None:
    """Through panelCondPost, in the values each generation takes.

    A mode the panel does not have raises before anything is sent.
    """
    api = make_api()
    assert api.set_mode(LupusecAlarmMode.Home) is True
    api.rest.panel_cond_post.assert_called_once_with(1, vendor_api.MODE_HOME1)
    with pytest.raises(LupusecNotSupportedException):
        api.set_mode(LupusecAlarmMode.AlarmTriggered)

    xt1 = make_api(legacy=True)
    assert xt1.set_mode(LupusecAlarmMode.Disarmed) is True
    xt1.rest.panel_cond_post.assert_called_once_with(undocumented_legacy_api.MODE_DISARM)
    with pytest.raises(LupusecNotSupportedException):
        xt1.set_mode(LupusecAlarmMode.AlarmTriggered)


def test_a_refused_mode_is_not_written_into_the_alarm() -> None:
    """The alarm device used to take the new mode whatever the panel said."""
    from lupupy.devices.alarm import LupusecAlarm

    alarm = LupusecAlarm({"device_id": "0", "type": "Alarm", "mode": "Disarm"})
    api = MagicMock()
    api.set_mode.return_value = False

    assert alarm.set_home(api) is False
    assert alarm.mode is LupusecAlarmMode.Disarmed

    api.set_mode.return_value = True
    assert alarm.set_home(api) is True
    assert alarm.mode is LupusecAlarmMode.Home
    api.set_mode.assert_called_with(LupusecAlarmMode.Home)


def test_power_switches_are_numbered_per_form() -> None:
    """The id was built from the number of known devices and moved with it."""
    api = make_api(legacy=True)
    api.rest.pss_status_get.return_value = {
        "forms": {
            "pss1": {"ready": 1, "pssonoff": "on", "name": "Lamp"},
            "pss2": {"ready": 0, "pssonoff": "off", "name": "Unused"},
            "pss3": {"ready": 1, "pssonoff": "off", "name": "Heater"},
        }
    }

    switches = api.get_power_switches()

    assert [(s["device_id"], s["name"]) for s in switches] == [
        ("pss1", "Lamp"),
        ("pss3", "Heater"),
    ]


def test_the_device_list_is_read_once_per_moment() -> None:
    """Refreshing each device asks for the whole list."""
    api = make_api()
    api.rest.device_list_get.return_value = {"senrows": []}

    api.get_sensors()
    api.get_sensors()

    api.rest.device_list_get.assert_called_once()


def test_connecting_uses_the_configured_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """The user says which panel it is; nothing is asked of it to find out."""
    rest, legacy = MagicMock(), MagicMock()
    monkeypatch.setattr(api_package, "UndocumentedApi", lambda *args: rest)
    monkeypatch.setattr(api_package, "UndocumentedLegacyApi", lambda *args: legacy)
    monkeypatch.setattr(current_helper, "_load_history_cache", list)

    connected = {
        model: api_package.connect("user", "secret", "panel.lan", model)
        for model in LupusecModel
    }

    assert {m.value: type(api).__name__ for m, api in connected.items()} == {
        "XT1": "LegacyLupusecApi",
        "XT1 Plus": "LupusecApi",
        "XT2": "LupusecApi",
        "XT2 Plus": "LupusecApi",
        "XT3": "LupusecApi",
        "XT4": "LupusecApi",
    }
    assert connected[LupusecModel.XT1].generation is LupusecModelType.XT1_Legacy
    assert connected[LupusecModel.XT3].model is LupusecModel.XT3
    assert rest.method_calls == []
    assert [c[0] for c in legacy.method_calls] == ["sensor_list_get", "login_post"]
