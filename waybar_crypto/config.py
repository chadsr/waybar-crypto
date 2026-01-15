import configparser
import os
from typing import TypedDict

from .exceptions import NoApiKeyException, WaybarCryptoException

FLOAT_FORMATTER = "{val:.{dp}f}"

COIN_PRECISION_OPTIONS: set[str] = set(
    [
        "price_precision",
        "change_precision",
        "volume_precision",
    ]
)
FORMAT_OPTION_PREFIX = "format_"

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
DEFAULT_PRECISION = 2
MIN_PRECISION = 0

API_KEY_ENV = "COINMARKETCAP_API_KEY"


class ConfigGeneral(TypedDict):
    currency: str
    currency_symbol: str
    spacer_symbol: str
    display_options: list[str]
    display_options_format: dict[str, str]
    api_key: str


class ConfigCoin(TypedDict, total=False):
    icon: str
    in_tooltip: bool
    price_precision: int
    change_precision: int
    volume_precision: int
    display_options_format: dict[str, str]


class Config(TypedDict):
    """Parsed configuration file"""

    general: ConfigGeneral
    coins: dict[str, ConfigCoin]


def read_config(config_path: str) -> Config:
    """Read a configuration file

    Args:
        config_path (str): Path to a .ini configuration file

    Returns:
        Config: Configuration dict object
    """

    cfp = configparser.ConfigParser(allow_no_value=True, interpolation=None)  # noqa: F821
    cfp.optionxform = str  # Preserve case for section names and options

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
        coin_symbol = coin_name  # Preserve original case for API compatibility
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

        # Parse per-coin format overrides
        coin_formats: dict[str, str] = {}
        for display_key in DEFAULT_DISPLAY_OPTIONS_FORMAT:
            format_option = f"{FORMAT_OPTION_PREFIX}{display_key}"
            if format_option in cfp[coin_name]:
                coin_formats[display_key] = cfp.get(coin_name, format_option)

        if coin_formats:
            coins[coin_symbol]["display_options_format"] = coin_formats

    # The fiat currency used in the trading pair
    currency = cfp.get("general", "currency").upper()
    currency_symbol = cfp.get("general", "currency_symbol")

    spacer_symbol = ""
    if "spacer_symbol" in cfp["general"]:
        spacer_symbol = cfp.get("general", "spacer_symbol")

    # Get a list of the chosen display options
    display_options: list[str] = []
    display_options_str = cfp.get("general", "display")
    if display_options_str:
        display_options = display_options_str.split(",")

    if not display_options:
        display_options = DEFAULT_DISPLAY_OPTIONS

    for display_option in display_options:
        if display_option not in DEFAULT_DISPLAY_OPTIONS_FORMAT:
            raise WaybarCryptoException(f"invalid display option '{display_option}'")

    # Start with a copy of default formats
    display_options_format = DEFAULT_DISPLAY_OPTIONS_FORMAT.copy()
    display_format_price = display_options_format["price"]
    display_options_format["price"] = f"{currency_symbol}{display_format_price}"

    # Parse global format overrides from [general] section
    for display_key in DEFAULT_DISPLAY_OPTIONS_FORMAT:
        format_option = f"{FORMAT_OPTION_PREFIX}{display_key}"
        if format_option in cfp["general"]:
            display_options_format[display_key] = cfp.get("general", format_option)

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
