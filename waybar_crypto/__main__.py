import json
import os
import sys
from argparse import ArgumentParser, Namespace
from typing import TypedDict

from . import __version__
from .config import read_config
from .exceptions import WaybarCryptoException
from .waybar_crypto import WaybarCrypto

XDG_CONFIG_HOME_ENV = "XDG_CONFIG_HOME"
DEFAULT_XDG_CONFIG_HOME_PATH = "~/.config"
CONFIG_DIR = "waybar-crypto"
CONFIG_FILE = "config.ini"


class Args(TypedDict):
    config_path: str


def parse_args() -> Args:
    parser: ArgumentParser = ArgumentParser()

    _ = parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
        help="Show version and exit",
    )

    # Utilise XDG_CONFIG_HOME if it exists
    xdg_config_home_path = os.getenv(XDG_CONFIG_HOME_ENV)
    if not xdg_config_home_path:
        xdg_config_home_path = DEFAULT_XDG_CONFIG_HOME_PATH

    default_config_path = os.path.join(xdg_config_home_path, CONFIG_DIR, CONFIG_FILE)
    _ = parser.add_argument(
        "-c",
        "--config-path",
        type=str,
        default=default_config_path,
        help=f"Path to the configuration file (default: '{default_config_path}')",
    )

    parsed_ns: Namespace = parser.parse_args()
    args: Args = Args(**vars(parsed_ns))  # pyright: ignore[reportAny]

    return args


def main():
    args: Args = parse_args()
    abs_config_path = os.path.expanduser(args["config_path"])  # expand ~ if present
    if not os.path.isfile(abs_config_path):
        raise WaybarCryptoException(f"configuration file not found at '{abs_config_path}'")

    config = read_config(abs_config_path)
    waybar_crypto = WaybarCrypto(config)
    quotes_latest = waybar_crypto.coinmarketcap_latest()
    output = waybar_crypto.waybar_output(quotes_latest)

    # Write the output dict as a json string to stdout
    _ = sys.stdout.write(json.dumps(output))


if __name__ == "__main__":
    main()
