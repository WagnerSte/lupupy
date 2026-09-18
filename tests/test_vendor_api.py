"""Tests for the layers between the panel and the library.

The facades have one method per REST action: VendorApi for the actions the
manufacturer documents, UndocumentedApi for those worked out by watching an
XT1 Plus, UndocumentedLegacyApi for those of the first XT1. The helpers use a facade
and nothing below it, and everything about the first XT1 stays in its own
facade and helper.
"""

import inspect
import re
from pathlib import Path

import lupupy
import lupupy.lupusec
from lupupy.api.legacy.undocumented_legacy_api import UndocumentedLegacyApi
from lupupy.api.current.helper import LupusecApi
from lupupy.api.legacy.helper import LegacyLupusecApi
from lupupy.api.transport import Transport
from lupupy.api.current.undocumented_api import UndocumentedApi
from lupupy.api.current.vendor_api import VendorApi

REACHING_PAST = r"\bsession\b|\brequests\.|self\.rest\._\w+|_request\(|_send\(|_decode\("


def own_methods(cls: type, base: type | None = None) -> dict[str, object]:
    """The functions a class defines itself, beyond those of base."""
    inherited = set(vars(base)) if base else set()
    return {
        name: member
        for name, member in vars(cls).items()
        if callable(member) and not name.startswith("__") and name not in inherited
    }


def actions(cls: type) -> set[str]:
    """The REST actions a facade offers, inherited ones included."""
    return {
        name
        for name, _ in inspect.getmembers(cls, inspect.isfunction)
        if not name.startswith("_")
    }


def rest_calls(source: str) -> set[str]:
    return set(re.findall(r"self\.rest\.(\w+)\(", source))


def test_the_documented_facade_is_the_document() -> None:
    """Six actions, named after them, none claiming to be reverse engineered."""
    assert {n for n in own_methods(VendorApi) if not n.startswith("_")} == {
        "token_get",
        "device_list_get",
        "device_list_pss_get",
        "device_switch_pss_post",
        "panel_cond_get",
        "panel_cond_post",
    }
    assert not any(
        hasattr(m, "undocumented_source") for m in own_methods(VendorApi).values()
    )
    assert not hasattr(VendorApi, "undocumented_source")


def test_everything_beyond_the_document_says_where_it_comes_from() -> None:
    """A firmware update is free to break these, so each says so.

    Both facades are flagged as a whole and every action on its own, and
    each is named after its REST action.
    """
    for facade, base in ((UndocumentedApi, VendorApi), (UndocumentedLegacyApi, Transport)):
        assert hasattr(facade, "undocumented_source"), facade
        added = own_methods(facade, base)
        assert {n for n, m in added.items() if not hasattr(m, "undocumented_source")} == set(), facade
        assert {
            n
            for n in added
            if not n.startswith("_") and not re.search(r"_(get|post)(_|$)", n)
        } == set(), facade


def test_the_helpers_go_through_their_facade_only() -> None:
    """A helper talks HTTP only by calling an action of its own facade."""
    for helper, facade in ((LupusecApi, UndocumentedApi), (LegacyLupusecApi, UndocumentedLegacyApi)):
        source = inspect.getsource(helper)
        assert re.findall(REACHING_PAST, source) == [], helper
        assert rest_calls(source) <= actions(facade), rest_calls(source) - actions(facade)


def test_the_first_xt1_stays_in_its_own_facade_and_helper() -> None:
    """No branch on the model outside the legacy helper.

    Every helper method that needs an action the first XT1 does not have is
    overridden by the legacy helper, so it never reaches for one.
    """
    for module_or_class in (LupusecApi, lupupy.lupusec):
        source = inspect.getsource(module_or_class)
        assert not re.search(r"XT1_Legacy|\.model\s*[!=]=|legacy", source), module_or_class

    missing = {
        name
        for name, method in own_methods(LupusecApi).items()
        if rest_calls(inspect.getsource(method)) - actions(UndocumentedLegacyApi)
        and name not in vars(LegacyLupusecApi)
    }
    assert missing == set()


def test_the_legacy_folder_can_be_taken_out() -> None:
    """Nothing but connect() and the legacy folder itself imports from it.

    The first XT1's helper builds on the current one, never the other way
    round, so dropping support for it means deleting lupupy/api/legacy and
    one branch in connect().
    """
    package = Path(lupupy.__file__).parent
    allowed = {package / "api" / "__init__.py", *(package / "api" / "legacy").glob("*.py")}
    importers = {
        path
        for path in package.rglob("*.py")
        if "__pycache__" not in path.parts
        and re.search(r"^\s*(from|import) lupupy\.api\.legacy", path.read_text(), re.M)
    }

    assert {p.relative_to(package) for p in importers - allowed} == set()
