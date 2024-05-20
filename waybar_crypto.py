#!/usr/bin/env python3

import sys
import os
from typing import TypedDict
import requests
import json
import configparser

API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
API_KEY_ENV = "COINMARKETCAP_API_KEY"
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
DISPLAY_OPTIONS_FORMAT: dict[str, str] = {
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

TIMEOUT_SECONDS = 10


class ConfigGeneral(TypedDict):
    currency: str
    currency_symbol: str
    display_options: list[str]
    display_options_format: dict[str, str]
    api_key: str


class ConfigCoin(TypedDict):
    icon: str
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
    data: QuoteData


class WaybarCryptoException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class CoinmarketcapApiException(WaybarCryptoException):
    def __init__(self, message: str, error_code: int | None) -> None:
        super().__init__(message)
        self.error_code = error_code

    def __str__(self) -> str:
        return f"{self.message} ({self.error_code})"


class WaybarCrypto(object):
    def __init__(self, config_path: str):
        self.config: Config = self.__parse_config_path(config_path)

    def __parse_config_path(self, config_path: str) -> Config:
        # Attempt to load crypto.ini configuration file
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
            if coin_name in coins:
                # duplicate entry, skip
                continue

            coins[coin_name] = {
                "icon": cfp[coin_name]["icon"],
                "price_precision": DEFAULT_PRECISION,
                "change_precision": DEFAULT_PRECISION,
                "volume_precision": DEFAULT_PRECISION,
            }

            for coin_precision_option in COIN_PRECISION_OPTIONS:
                if coin_precision_option in cfp[coin_name]:
                    if not cfp[coin_name][coin_precision_option].isdigit():
                        raise WaybarCryptoException(
                            f"configured option '{coin_precision_option}' for cryptocurrency '{coin_name}' must be an integer"
                        )

                    precision_value = int(cfp[coin_name][coin_precision_option])
                    if precision_value < MIN_PRECISION:
                        raise WaybarCryptoException(
                            f"value of option '{coin_precision_option}' for cryptocurrency '{coin_name}' must be greater than {MIN_PRECISION}",
                        )

                    coins[coin_name][coin_precision_option] = precision_value

        # The fiat currency used in the trading pair
        currency = cfp["general"]["currency"].upper()
        currency_symbol = cfp["general"]["currency_symbol"]

        # Get a list of the chosen display options
        display_options: list[str] = cfp["general"]["display"].split(",")

        if len(display_options) == 0:
            display_options = DEFAULT_DISPLAY_OPTIONS

        for display_option in display_options:
            if display_option not in DISPLAY_OPTIONS_FORMAT:
                raise WaybarCryptoException(f"invalid display option '{display_option}")

        display_options_format = DISPLAY_OPTIONS_FORMAT
        display_options_format["price"] = (
            f"{currency_symbol}{display_options_format["price"]}"
        )

        api_key: str | None = None
        if "api_key" in cfp["general"]:
            api_key = cfp["general"]["api_key"]

        # If API_KEY_ENV exists, take precedence over the config file value
        api_key = os.getenv(key=API_KEY_ENV, default=api_key)
        if api_key is None:
            raise WaybarCryptoException(
                f"no API key provided in configuration file or with environment variable '{API_KEY_ENV}'"
            )

        config: Config = {
            "general": {
                "currency": currency,
                "currency_symbol": currency_symbol,
                "display_options": display_options,
                "display_options_format": display_options_format,
                "api_key": api_key,
            },
            "coins": coins,
        }

        return config

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

        output_obj: WaybarOutput = {
            "text": "",
            "tooltip": "Cryptocurrency metrics from Coinmarketcap:\n",
            "class": CLASS_NAME,
        }

        # For each coin, populate our output_obj
        # with a string according to the display_options
        for i, (coin_name, coin_config) in enumerate(self.config["coins"].items()):
            icon = coin_config["icon"]
            price_precision = coin_config["price_precision"]
            volume_precision = coin_config["volume_precision"]
            change_precision = coin_config["change_precision"]

            # Extract the object relevant to our coin/currency pair
            pair_info = quotes_latest["data"][coin_name.upper()]["quote"][currency]

            output = f"{icon}"
            if i > 0:
                output = f" {output}"

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

            output_obj["text"] += output
            output_obj["tooltip"] += output

        return output_obj


def main():
    # Get the absolute path of this script
    abs_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = f"{abs_dir}/{CONFIG_FILE}"

    waybar_crypto = WaybarCrypto(config_path)
    quotes_latest = waybar_crypto.coinmarketcap_latest()
    output = waybar_crypto.waybar_output(quotes_latest)

    # Write the output dict as a json string to stdout
    sys.stdout.write(json.dumps(output))


if __name__ == "__main__":
    main()
