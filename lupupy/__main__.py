"""Command line utility for Lupupy."""

import argparse
import json
import logging
import os

from lupupy import constants as CONST
from lupupy.lupusec import Lupusec
from lupupy.devices import LupusecDevice

_LOGGER = logging.getLogger("lupuseccl")


def setup_logging(log_level: int = logging.INFO) -> None:
    """Set up the logging."""
    logging.basicConfig(level=log_level)
    fmt = "%(asctime)s %(levelname)s (%(threadName)s) " "[%(name)s] %(message)s"
    colorfmt = f"%(log_color)s{fmt}%(reset)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # Suppress overly verbose logs from libraries that aren't helpful
    logging.getLogger("requests").setLevel(logging.WARNING)

    try:
        from colorlog import ColoredFormatter

        logging.getLogger().handlers[0].setFormatter(
            ColoredFormatter(
                colorfmt,
                datefmt=datefmt,
                reset=True,
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red",
                },
            )
        )
    except ImportError:
        pass

    logger = logging.getLogger("")
    logger.setLevel(log_level)


def get_arguments() -> argparse.Namespace:
    """Get parsed arguments."""
    parser = argparse.ArgumentParser("Lupupy: Command Line Utility")

    parser.add_argument("-u", "--username", help="Username", required=False)

    parser.add_argument("-p", "--password", help="Password", required=False)

    parser.add_argument(
        "--arm",
        help="Arm alarm to mode",
        required=False,
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-i", "--ip_address", help="IP of the Lupus panel", required=False
    )

    parser.add_argument(
        "--disarm",
        help="Disarm the alarm",
        required=False,
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--home",
        help="Set to home mode",
        required=False,
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--devices",
        help="Output all devices",
        required=False,
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--history",
        help="Get the history",
        required=False,
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--status",
        help="Get the status of the panel",
        required=False,
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--debug",
        help="Enable debug logging",
        required=False,
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--quiet",
        help="Output only warnings and errors",
        required=False,
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--version",
        "-v",
        help="Shows lupupy version",
        required=False,
        default=False,
        action="store_true",
    )

    return parser.parse_args()


def call(args: argparse.Namespace) -> None:
    """Execute command line helper."""

    if args.version:
        _LOGGER.info(CONST.VERSION)
        return

    # Arguments on the command line are visible to every process on the
    # machine, so the environment is offered as the safer alternative.
    username = args.username or os.environ.get("LUPUS_USER")
    password = args.password or os.environ.get("LUPUS_PASSWORD")
    ip_address = args.ip_address or os.environ.get("LUPUS_IP")

    if not username or not password or not ip_address:
        # SystemExit gives a readable message and a non-zero exit code,
        # where a bare exception would print a traceback.
        raise SystemExit(
            "Please supply a username, password and ip, either as arguments or "
            "as LUPUS_USER, LUPUS_PASSWORD and LUPUS_IP in the environment."
        )

    def _devicePrint(dev: LupusecDevice, append: str = "") -> None:
        _LOGGER.info("%s%s", dev.desc, append)

    try:
        lupusec = Lupusec(
            ip_address=ip_address,
            username=username,
            password=password,
        )

        if args.arm:
            if lupusec.get_alarm().set_away(lupusec.api):
                _LOGGER.info("Alarm mode changed to armed")
            else:
                _LOGGER.warning("Failed to change alarm mode to armed")

        if args.disarm:
            if lupusec.get_alarm().set_standby(lupusec.api):
                _LOGGER.info("Alarm mode changed to disarmed")
            else:
                _LOGGER.warning("Failed to change alarm mode to disarmed")

        if args.home:
            if lupusec.get_alarm().set_home(lupusec.api):
                _LOGGER.info("Alarm mode changed to home")
            else:
                _LOGGER.warning("Failed to change alarm mode to home")

        if args.history:
            _LOGGER.info(json.dumps(lupusec.get_history(), indent=4, sort_keys=True))

        if args.status:
            _LOGGER.info("Mode of panel: %s", lupusec.get_alarm().mode)

        if args.devices:
            for device in lupusec.get_devices():
                _devicePrint(device)

    except Exception as exc:
        _LOGGER.error(exc)
    finally:
        _LOGGER.info("--Finished running--")


def main() -> None:
    """Execute from command line."""
    args = get_arguments()

    if args.debug:
        log_level = logging.DEBUG
    elif args.quiet:
        log_level = logging.WARN
    else:
        log_level = logging.INFO

    setup_logging(log_level)
    call(args)


if __name__ == "__main__":
    main()
