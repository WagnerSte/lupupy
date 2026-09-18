"""Tests for the REST facade and the helpers built on it."""

import json
import logging
import time
from datetime import datetime, timezone
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

    rest.session.get.return_value = answer('{"arearows": {"1": "1 Haus"}}')
    assert rest.area_list_get() == {"arearows": {"1": "1 Haus"}}


def test_switching_always_sends_pd() -> None:
    """A socket ignores deviceSwitchPSSPost without pd; empty means for good."""
    api = make_api()

    assert api.switch("ZS:01", True) is True
    assert api.switch("ZS:01", False) is True
    assert api.move_shutter("ZS:19", vendor_api.SHUTTER_STOP) is True
    assert api.rest.device_switch_pss_post.call_args_list == [
        call("ZS:01", switch=vendor_api.SWITCH_ON, pd=""),
        call("ZS:01", switch=vendor_api.SWITCH_OFF, pd=""),
        call("ZS:19", switch=vendor_api.SHUTTER_STOP, pd=""),
    ]

    api.rest.device_switch_pss_post.return_value = {"result": 0, "message": "no"}
    assert api.move_shutter("ZS:19", vendor_api.SHUTTER_UP) is False


def test_arming_an_area() -> None:
    """Areas 1 and 2 and all three home modes, through panelCondPost.

    The first XT1 knows a single area, one home mode and numbers its modes
    differently. A mode or area the panel does not have raises before
    anything is sent.
    """
    api = make_api()

    assert api.set_mode(LupusecAlarmMode.Home2, area=2) is True
    assert api.set_mode(LupusecAlarmMode.Home3) is True
    assert api.rest.panel_cond_post.call_args_list == [
        call(2, vendor_api.MODE_HOME2),
        call(1, vendor_api.MODE_HOME3),
    ]
    for mode, area in ((LupusecAlarmMode.AlarmTriggered, 1), (LupusecAlarmMode.Home, 3)):
        with pytest.raises(LupusecNotSupportedException):
            api.set_mode(mode, area=area)
    assert api.rest.panel_cond_post.call_count == 2

    xt1 = make_api(legacy=True)
    for mode, area in ((LupusecAlarmMode.Home, 2), (LupusecAlarmMode.Home2, 1)):
        with pytest.raises(LupusecNotSupportedException):
            xt1.set_mode(mode, area=area)
    assert xt1.set_mode(LupusecAlarmMode.Disarmed) is True
    xt1.rest.panel_cond_post.assert_called_once_with(undocumented_legacy_api.MODE_DISARM)


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
    api.set_mode.assert_called_with(LupusecAlarmMode.Home, area=1)


def test_area_names_come_from_the_panel() -> None:
    """The panel puts the area number in front of each name for display.

    Only that prefix is taken off, so a name that starts with a number of
    its own keeps it.
    """
    api = make_api()
    api.rest.area_list_get.return_value = {
        "arearows": {"1": "1 Haus", "2": "2 Keller", "3": "2. Etage"}
    }

    assert api.get_area_names() == {1: "Haus", 2: "Keller", 3: "2. Etage"}


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


def test_events_are_parsed() -> None:
    """The rows arrive with placeholders, tabs and timestamps as strings.

    A system event carries no device, and its user does.
    """
    events = make_api().get_events()

    assert events[-1] == {
        "uid": 8858,
        "time": datetime(2026, 9, 15, 22, 35, 15, tzinfo=timezone.utc),
        "area": "1",
        "zone": 2,
        "device_id": "RF:00000001",
        "device_type": 9,
        "name": "Hallway",
        "category": 1,
        "code": 183,
        "value": "1",
        "user": None,
    }
    assert (events[1]["zone"], events[1]["device_id"], events[1]["device_type"]) == (
        None,
        None,
        None,
    )
    assert events[1]["user"] == "{WEB_MSG_USER_ID}1(user)"


def test_events_continue_where_the_caller_left_off(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The panel keeps a limited number of entries, so a uid can fall out."""
    seen = {
        after_uid: [e["uid"] for e in make_api().get_events(after_uid)]
        for after_uid in (None, 8857, 8858)
    }

    assert seen == {None: [8856, 8857, 8858], 8857: [8858], 8858: []}

    with caplog.at_level(logging.WARNING):
        make_api().get_events(8855)
    assert caplog.text == ""

    with caplog.at_level(logging.WARNING):
        make_api().get_events(8800)
    assert "8800" in caplog.text



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


def test_panel_info_is_what_welcome_get_reports() -> None:
    """Asked on demand, not to tell which panel it is."""
    api = make_api()
    api.rest.welcome_get.return_value = {
        "updates": {
            "version": "HPGW-G1 0.0.3.7J HPGW-L2-XA35H ",
            "rf_ver": "HPGW-L2-XA35H",
            "zbs_ver": "4.1.2.6.2",
            "gsm_ver": "",
            "mac": "00:1D:94:00:00:01",
        }
    }

    info = api.get_panel_info()

    assert (info.firmware, info.version, info.zigbee, info.gsm) == (
        "0.0.3.7J",
        "HPGW-G1 0.0.3.7J HPGW-L2-XA35H",
        "4.1.2.6.2",
        "",
    )


def test_what_the_first_xt1_cannot_do_raises() -> None:
    """The calling application decides what to do about it, not the library."""
    xt1 = make_api(legacy=True)

    for name, call_it in {
        "switch": lambda: xt1.switch("ZS:01", True),
        "move_shutter": lambda: xt1.move_shutter("ZS:01", vendor_api.SHUTTER_UP),
        "get_events": xt1.get_events,
        "get_area_names": xt1.get_area_names,
        "get_panel_info": xt1.get_panel_info,
    }.items():
        with pytest.raises(LupusecNotSupportedException):
            call_it()
        assert issubclass(LupusecNotSupportedException, LupusecException), name

    assert xt1.rest.method_calls == []
