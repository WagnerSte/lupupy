# Lupupy

A python3 library to communicate with the Lupus Electronics alarm control panel.

## Disclaimer:

Published under the MIT license - See LICENSE file for more details.

"Lupusec" is a trademark owned by Lupusec Electronics, see www.lupus-electronics.de for more information. I am in no way affiliated with Lupus Electronics.

## Installation

You can install the library with pip:
```
pip install Lupupy
```

## Usage

You can integrate the library into your own project, or simply use it in the command line.
```
lupupy -u USERNAME -p PASSWORD -i IP_ADDRESS -m "XT1 Plus" --devices
```
This will retrieve a simple list of all devices.

The model is the panel as it says on the device: XT1, XT1 Plus, XT2, XT2 Plus,
XT3 or XT4. The library does not find it out by itself, since the first XT1
speaks a different web API from all later panels. In code:

```python
from lupupy import Lupusec, LupusecModel

system = Lupusec("USERNAME", "PASSWORD", "IP_ADDRESS", LupusecModel.XT1_PLUS)
```

What a panel cannot do, such as switching on the first XT1 or a second area
where there is none, raises `LupusecNotSupportedException`.

Arguments are visible to every process on the machine, so credentials can also
be supplied through the environment, or through an env file:

```
cp .env.example .env
chmod 600 .env          # it holds your panel password
$EDITOR .env

lupupy --devices
```

`.env` is read from the current directory. Use `--env-file PATH` or the
`LUPUS_ENV_FILE` variable to point somewhere else. Values already set in the
environment are never overridden by the file, and `.env` is ignored by git.

## Testing against a real panel

Every panel is configured differently, so besides the unit tests there is only
one integration test, and it is opt-in (see below). The command line utility is
the quickest way to check a change against real hardware.

Read-only commands, safe to run at any time:

```
lupupy --status         # the mode the panel is in
lupupy --devices        # every device the panel reports
lupupy --history        # the event log
lupupy --devices --debug  # with the raw requests and responses
```

Commands that change the state of the alarm system:

```
lupupy --arm            # arm
lupupy --home           # arm in home mode
lupupy --disarm         # disarm
```

Arming a panel with an open contact sets off the siren, so check `--status` and
`--devices` first. A typical session while working on the library:

```
pip install -e .
lupupy --status                  # before
lupupy --devices | grep -i door
lupupy --disarm
lupupy --status                  # after
```

Please mention the panel model and firmware you verified against when opening a
pull request. `lupupy --devices --debug` prints both.

### The integration test

`tests/test_hardware.py` walks a real panel through its modes and reads the
state back at every step: disarmed, home, disarmed. It is deselected by
default and needs two things to run:

```
cp .env.example .env && chmod 600 .env   # panel, credentials and the opt-in
pytest -m hardware
```

`.env.example` carries `LUPUS_HARDWARE_TEST` commented out. Uncommenting it is
the opt-in, and the marker keeps these tests out of an ordinary `pytest` run
either way.

The test reads `.env` the same way the command line does, so `--env-file`'s
counterpart works here as well:

```
LUPUS_HARDWARE_TEST=1 LUPUS_ENV_FILE=~/my-panel.env pytest -m hardware
```

It arms a real alarm system, so read this first:

- **The panel must be disarmed** when the test starts, and it is always put
  back to disarmed afterwards, including when a step fails.
- **Open contacts abort the run.** The test skips rather than arm a panel
  that would immediately sound the siren. Bypassed zones are ignored, as the
  panel ignores them too.
- **Every mode change is reported** through whatever the panel is configured
  to notify, including a monitoring service over Contact ID. Those are real
  events on somebody's screen.
- **Arming in away mode activates the motion detectors.** Anybody moving in a
  covered room sets off the siren while the panel is armed, so pick a quiet
  moment.

The test waits for the panel to reach each mode instead of sleeping for a
fixed time, because entry and exit delays are configurable per installation.

---

## Supported panels and devices

The model is configured, not detected. The XT1 Plus and all later panels share
one web API, with two areas and three home modes; the first XT1 speaks an API
of its own, with a single area and one home mode, and what it cannot do raises
`LupusecNotSupportedException`.

| | XT1 | XT1 Plus | XT2 | XT3 | XT4 |
|---|:---:|:---:|:---:|:---:|:---:|
| Home, Arm and Disarm for all Areas | (🟡) | ✅ | (🟡) | (🟡) | (🟡) |
| Telling that an alarm went off | (🟡) | ✅ | (🟡) | (🟡) | (🟡) |
| Door and window contacts | (🟡) | ✅ | (🟡) | (🟡) | (🟡) |
| Motion detectors, recognised with diagnostics | ❌ | ✅ | (🟡) | (🟡) | (🟡) |
| Motion detectors, movement in the event log¹ | ❌ | ✅ | (🟡) | (🟡) | (🟡) |
| Smoke detectors | (🟡) | ✅ | (🟡) | (🟡) | (🟡) |
| Water sensors | (🟡) | (🟡) | (🟡) | (🟡) | (🟡) |
| Sirens, keypads, remote controls, status displays, scene switches | ❌ | ✅ | (🟡) | (🟡) | (🟡) |
| Battery, tamper, bypass and signal strength of a device | (🟡) | ✅ | (🟡) | (🟡) | (🟡) |
| Sockets: state | (🟡) | ✅ | (🟡) | (🟡) | (🟡) |
| Sockets: switching | ❌ | ✅ | (🟡) | (🟡) | (🟡) |
| Roller shutters: up, down, stop | ❌ | ✅ | (🟡) | (🟡) | (🟡) |
| Roller shutters: moving to a position | ❌ | ❌ | ❌ | ❌ | ❌ |
| Panel condition: mains power, radio interference, GSM, open contact | ❌ | ✅ | (🟡) | (🟡) | (🟡) |
| Event log | ❌ | ✅ | (🟡) | (🟡) | (🟡) |
| Area names | ❌ | ✅ | (🟡) | (🟡) | (🟡) |
| What each kind of device can do | ❌ | ✅ | (🟡) | (🟡) | (🟡) |
| Firmware and radio modules | ❌ | ✅ | (🟡) | (🟡) | (🟡) |

✅ tested on a panel &nbsp;·&nbsp; (🟡) supported, not tested &nbsp;·&nbsp; ❌ not supported

¹ A motion detector does not change its state in the device list when it sees
movement. The panel writes the movement to its event log, where `get_events()`
reads it, but only for a zone set up to react while disarmed: a detector set up
as a door chime shows up as "door chime" (code 4) with its zone and name, one
without such a reaction leaves no trace. While armed, movement raises an alarm
instead.

The panels of one generation run the same code, so a feature tested on an
XT1 Plus is expected to work on the later panels as well; it is only marked
tested once someone has tried it there. Please report what works on yours.

Which calls come from the manufacturer's API document and which were worked out
by watching the panel is marked in the code, see `lupupy/api`.

## Acknowledgements

Lupupy is strongly inspired by [abodepy](https://github.com/MisterWil/abodepy),
the library for Abode alarm systems by [MisterWil](https://github.com/MisterWil),
and started out from it. The idea of a system object holding devices of different kinds, and much of the
code of the first versions of this library, came from there and was adapted to
Lupus panels. It has been rewritten for the Lupus web API since, but the shape
still shows where it came from.

Many thanks to MisterWil for abodepy, and for publishing it openly so that it
could become the starting point for this library.
