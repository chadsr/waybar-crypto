#!/usr/bin/env python3

import sys
import os
from typing import TypedDict
import requests
import json
import configparser
import argparse

API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
API_KEY_ENV = "COINMARKETCAP_API_KEY"

XDG_CONFIG_HOME_ENV = "XDG_CONFIG_HOME"
DEFAULT_XDG_CONFIG_HOME_PATH = "~/.config"
CONFIG_DIR = "waybar-crypto"
CONFIG_FILE = "config.ini"

DEFAULT_PRECISION = 2
MIN_PRECISION = 0

CLASS_NAME = "crypto"

COIN_PRECISION_OPTIONS: set[str] = set(
    [
        "price_precision",
        "change_precision",
        "volume_precision",
    ]
)

FLOAT_FORMATTER = "{val:.{dp}f}"
DEFAULT_DISPLAY_OPTIONS_FORMAT: dict[str, str] = {
    "price": f"{FLOAT_FORMATTER}",
    "percent_change_1h": f"1h:{FLOAT_FORMATTER}%",
    "percent_change_24h": f"24h:{FLOAT_FORMATTER}%",
    "percent_change_7d": f"7d:{FLOAT_FORMATTER}%",
    "percent_change_30d": f"30d:{FLOAT_FORMATTER}%",
    "percent_change_60d": f"60d:{FLOAT_FORMATTER}%",
    "percent_change_90d": f"90d:{FLOAT_FORMATTER}%",
    "volume_24h": f"24hVol:{FLOAT_FORMATTER}",
    "volume_change_24h": f"24hVol:{FLOAT_FORMATTER}%",
}
DEFAULT_DISPLAY_OPTIONS: list[str] = ["price"]

DEFAULT_COIN_CONFIG_TOOLTIP = False

TIMEOUT_SECONDS = 10


class Args(TypedDict):
    config_path: str


class ConfigGeneral(TypedDict):
    currency: str
    currency_symbol: str
    spacer_symbol: str
    display_options: list[str]
    display_options_format: dict[str, str]
    api_key: str


class ConfigCoin(TypedDict):
    icon: str
    in_tooltip: bool
    price_precision: int
    change_precision: int
    volume_precision: int


class Config(TypedDict):
    """Parsed configuration file"""

    general: ConfigGeneral
    coins: dict[str, ConfigCoin]


WaybarOutput = TypedDict("WaybarOutput", {"text": str, "tooltip": str, "class": str})


class QuoteEntry(TypedDict):
    price: float
    volume_24h: float
    volume_change_24h: float
    percent_change_1h: float
    percent_change_24h: float
    percent_change_7d: float
    percent_change_30d: float
    percent_change_60d: float
    percent_change_90d: float
    last_updated: str


class QuoteData(TypedDict):
    """Quote data returned by the Coinmarketcap API"""

    id: int
    name: str
    symbol: str
    quote: dict[str, QuoteEntry]


class ResponseStatus(TypedDict):
    timestamp: str
    error_code: int
    error_message: str
    elapsed: int
    credit_count: int


class ResponseQuotesLatest(TypedDict):
    """Latest quotes response returns by the Coinmarketcap API"""

    status: ResponseStatus
    data: dict[str, QuoteData]


class WaybarCryptoException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NoApiKeyException(WaybarCryptoException):
    pass


class CoinmarketcapApiException(WaybarCryptoException):
    def __init__(self, message: str, error_code: int | None) -> None:
        super().__init__(message)
        self.error_code = error_code

    def __str__(self) -> str:
        return f"{self.message} ({self.error_code})"


def read_config(config_path: str) -> Config:
    """Read a configuration file

    Args:
        config_path (str): Path to a .ini configuration file

    Returns:
        Config: Configuration dict object
    """

    cfp = configparser.ConfigParser(allow_no_value=True, interpolation=None)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfp.read_file(f)
    except Exception as e:
        raise WaybarCryptoException(f"failed to open config file: {e}")

    # Assume any section that isn't 'general', is a coin
    coin_names = [section for section in cfp.sections() if section != "general"]

    # Construct the coin configuration dict
    coins: dict[str, ConfigCoin] = {}
    for coin_name in coin_names:
        coin_symbol = coin_name.upper()
        display_in_tooltip = DEFAULT_COIN_CONFIG_TOOLTIP
        if "in_tooltip" in cfp[coin_name]:
            display_in_tooltip = cfp.getboolean(coin_name, "in_tooltip")

        coins[coin_symbol] = {
            "icon": cfp.get(coin_name, "icon"),
            "in_tooltip": display_in_tooltip,
            "price_precision": DEFAULT_PRECISION,
            "change_precision": DEFAULT_PRECISION,
            "volume_precision": DEFAULT_PRECISION,
        }

        for coin_precision_option in COIN_PRECISION_OPTIONS:
            if coin_precision_option in cfp[coin_name]:
                precision_value = cfp.getint(coin_name, coin_precision_option)
                if precision_value < MIN_PRECISION:
                    raise WaybarCryptoException(
                        f"value of option '{coin_precision_option}' for cryptocurrency '{coin_name}' must be greater than {MIN_PRECISION}",
                    )

                coins[coin_symbol][coin_precision_option] = precision_value

    # The fiat currency used in the trading pair
    currency = cfp.get("general", "currency").upper()
    currency_symbol = cfp.get("general", "currency_symbol")

    spacer_symbol = ""
    if "spacer_symbol" in cfp["general"]:
        spacer_symbol = cfp.get("general", "spacer_symbol")

    # Get a list of the chosen display options
    display_options: list[str] = []
    display_options_str = cfp.get("general", "display")
    if display_options_str and len(display_options_str) > 0:
        display_options = display_options_str.split(",")

    if len(display_options) == 0:
        display_options = DEFAULT_DISPLAY_OPTIONS

    for display_option in display_options:
        if display_option not in DEFAULT_DISPLAY_OPTIONS_FORMAT:
            raise WaybarCryptoException(f"invalid display option '{display_option}'")

    display_options_format = DEFAULT_DISPLAY_OPTIONS_FORMAT
    display_format_price = display_options_format["price"]
    display_options_format["price"] = f"{currency_symbol}{display_format_price}"

    api_key: str | None = None
    if "api_key" in cfp["general"]:
        api_key = cfp.get("general", "api_key")
        if api_key == "":
            api_key = None

    # If API_KEY_ENV exists, take precedence over the config file value
    api_key = os.getenv(key=API_KEY_ENV, default=api_key)
    if api_key is None:
        raise NoApiKeyException(
            f"no API key provided in configuration file or with environment variable '{API_KEY_ENV}'"
        )

    config: Config = {
        "general": {
            "currency": currency,
            "currency_symbol": currency_symbol,
            "spacer_symbol": spacer_symbol,
            "display_options": display_options,
            "display_options_format": display_options_format,
            "api_key": api_key,
        },
        "coins": coins,
    }

    return config


class WaybarCrypto(object):
    def __init__(self, config: Config):
        if config["general"]["api_key"] == "":
            raise NoApiKeyException("No API key provided")

        self.config: Config = config

    def coinmarketcap_latest(self) -> ResponseQuotesLatest:
        # Construct API query parameters
        params = {
            "convert": self.config["general"]["currency"].upper(),
            "symbol": ",".join(coin.upper() for coin in self.config["coins"]),
        }

        # Add the API key as the expected header field
        headers = {
            "X-CMC_PRO_API_KEY": self.config["general"]["api_key"],
            "Accept": "application/json",
        }

        # Request the chosen price pairs
        try:
            response = requests.get(
                API_URL, params=params, headers=headers, timeout=TIMEOUT_SECONDS
            )
        except requests.exceptions.ConnectTimeout:
            raise WaybarCryptoException("request timed out")

        try:
            response_quotes_latest: ResponseQuotesLatest = response.json()
        except requests.exceptions.JSONDecodeError:
            raise WaybarCryptoException("could not parse API response body as JSON")

        if response.status_code != 200:
            response_status = response_quotes_latest["status"]
            error_code = None
            if "error_code" in response_status:
                error_code = response_status["error_code"]

            error_message = "coinmarketcap API error"
            if "error_message" in response_status:
                error_message = response_status["error_message"]

            raise CoinmarketcapApiException(error_message, error_code=error_code)

        return response_quotes_latest

    def waybar_output(self, quotes_latest: ResponseQuotesLatest) -> WaybarOutput:
        currency = self.config["general"]["currency"]
        display_options = self.config["general"]["display_options"]
        display_options_format = self.config["general"]["display_options_format"]
        spacer = self.config["general"]["spacer_symbol"]
        if spacer != "":
            spacer = f" {spacer}"

        output_obj: WaybarOutput = {
            "text": "",
            "tooltip": "",
            "class": CLASS_NAME,
        }

        # For each coin, populate our output_obj
        # with a string according to the display_options
        for coin_name, coin_config in self.config["coins"].items():
            icon = coin_config["icon"]
            price_precision = coin_config["price_precision"]
            volume_precision = coin_config["volume_precision"]
            change_precision = coin_config["change_precision"]

            # Extract the object relevant to our coin/currency pair
            pair_info = quotes_latest["data"][coin_name.upper()]["quote"][currency]

            output = f"{icon}"

            for display_option in display_options:
                precision = DEFAULT_PRECISION
                if "volume" in display_option:
                    precision = volume_precision
                elif "change" in display_option:
                    precision = change_precision
                elif "price" in display_option:
                    precision = price_precision

                value = round(pair_info[display_option], precision)
                output += f" {display_options_format[display_option]}".format(
                    dp=precision, val=value
                )

            if coin_config["in_tooltip"]:
                if output_obj["tooltip"] != "":
                    output = f"\n{output}"
                output_obj["tooltip"] += output
            else:
                if output_obj["text"] != "":
                    output = f"{spacer} {output}"
                output_obj["text"] += output

        return output_obj


def parse_args() -> Args:
    parser = argparse.ArgumentParser()

    # Utilise XDG_CONFIG_HOME if it exists
    xdg_config_home_path = os.getenv(XDG_CONFIG_HOME_ENV)
    if not xdg_config_home_path:
        xdg_config_home_path = DEFAULT_XDG_CONFIG_HOME_PATH

    default_config_path = os.path.join(xdg_config_home_path, CONFIG_DIR, CONFIG_FILE)
    parser.add_argument(
        "-c",
        "--config-path",
        type=str,
        default=default_config_path,
        help=f"Path to the configuration file (default: '{default_config_path}')",
    )
    args = parser.parse_args()

    return {"config_path": args.config_path}


def main():
    args = parse_args()

    config_path = os.path.expanduser(args["config_path"])
    if not os.path.isfile(config_path):
        raise WaybarCryptoException(f"configuration file not found at '{config_path}'")

    config = read_config(config_path)
    waybar_crypto = WaybarCrypto(config)
    quotes_latest = waybar_crypto.coinmarketcap_latest()
    output = waybar_crypto.waybar_output(quotes_latest)

    # Write the output dict as a json string to stdout
    sys.stdout.write(json.dumps(output))


if __name__ == "__main__":
    main()
