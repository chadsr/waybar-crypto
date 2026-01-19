import configparser
import os
from typing import TypedDict, TypeGuard, override
from typing import Required, NotRequired

from .exceptions import NoApiKeyException, WaybarCryptoException
from .models import DisplayOptionsFormatMap, DisplayOption


COIN_PRECISION_OPTIONS: set[str] = set(
    [
        "price_precision",
        "change_precision",
        "volume_precision",
    ]
)

FLOAT_FORMATTER = "{val:.{dp}f}"
DEFAULT_DISPLAY_OPTIONS_FORMAT: dict[DisplayOption, str] = {
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
DEFAULT_DISPLAY_OPTIONS: list[DisplayOption] = ["price"]
DEFAULT_COIN_CONFIG_TOOLTIP = False
DEFAULT_PRECISION = 2
MIN_PRECISION = 0
FORMAT_OPTION_PREFIX = "format_"

API_KEY_ENV = "COINMARKETCAP_API_KEY"


class ConfigGeneral(TypedDict):
    api_key: Required[str]
    currency_symbol: Required[str]
    currency: Required[str]
    display_options_format: Required[DisplayOptionsFormatMap]
    display_options: Required[list[DisplayOption]]
    spacer_symbol: Required[str]


class ConfigCoin(TypedDict, total=False):
    change_precision: Required[int]
    display_options_format: NotRequired[DisplayOptionsFormatMap]
    icon: Required[str]
    in_tooltip: Required[bool]
    price_precision: Required[int]
    volume_precision: Required[int]


class Config(TypedDict):
    """Parsed configuration file"""

    general: ConfigGeneral
    coins: dict[str, ConfigCoin]


class CaseConfigParser(configparser.ConfigParser):
    # Preserve case for option names (no lowercasing) with compatible signature
    @override
    def optionxform(self, optionstr: str) -> str:
        return optionstr


def read_config(config_path: str) -> Config:
    """Read a configuration file

    Args:
        config_path (str): Path to a .ini configuration file

    Returns:
        Config: Configuration dict object
    """

    cfp: CaseConfigParser = CaseConfigParser(
        allow_no_value=True,
        interpolation=None,
    )

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfp.read_file(f)
    except Exception as e:
        raise WaybarCryptoException(f"failed to open config file: {e}")

    api_key: str | None = cfp.get("general", "api_key", fallback=None)

    # If API_KEY_ENV exists, take precedence over the config file value
    api_key_env = os.getenv(key=API_KEY_ENV, default=api_key)
    if api_key_env:
        api_key = api_key_env

    if not api_key:
        raise NoApiKeyException(
            f"no API key provided in configuration file or with environment variable '{API_KEY_ENV}'"
        )

    # Assume any section that isn't 'general', is a coin
    sections: list[str] = cfp.sections()
    coin_names: list[str] = [name for name in sections if name != "general"]

    # Construct the coin configuration dict
    coins: dict[str, ConfigCoin] = {}
    for coin_name in coin_names:
        coin_name_str: str = coin_name
        coin_symbol: str = coin_name_str  # Preserve original case for API compatibility
        display_in_tooltip = DEFAULT_COIN_CONFIG_TOOLTIP
        if cfp.has_option(coin_name_str, "in_tooltip"):
            display_in_tooltip = cfp.getboolean(coin_name_str, "in_tooltip")

        coins[coin_symbol] = {
            "icon": cfp.get(coin_name_str, "icon"),
            "in_tooltip": display_in_tooltip,
            "price_precision": DEFAULT_PRECISION,
            "change_precision": DEFAULT_PRECISION,
            "volume_precision": DEFAULT_PRECISION,
        }

        for coin_precision_option in COIN_PRECISION_OPTIONS:
            if cfp.has_option(coin_name_str, coin_precision_option):
                precision_value = cfp.getint(coin_name_str, coin_precision_option)
                if precision_value < MIN_PRECISION:
                    raise WaybarCryptoException(
                        f"value of option '{coin_precision_option}' for cryptocurrency '{coin_name}' must be greater than {MIN_PRECISION}",
                    )

                coins[coin_symbol][coin_precision_option] = precision_value

        # Parse per-coin format overrides
        coin_formats: dict[DisplayOption, str] = {}
        for display_key in DEFAULT_DISPLAY_OPTIONS_FORMAT:
            format_option = f"{FORMAT_OPTION_PREFIX}{display_key}"
            if cfp.has_option(coin_name_str, format_option):
                coin_formats[display_key] = cfp.get(coin_name_str, format_option)

        # Only set overrides if any were provided for this coin
        if coin_formats:
            coins[coin_symbol]["display_options_format"] = coin_formats

    # The fiat currency used in the trading pair
    currency: str = cfp.get("general", "currency").upper()
    currency_symbol: str = cfp.get("general", "currency_symbol")

    spacer_symbol: str = ""
    if cfp.has_option("general", "spacer_symbol"):
        spacer_symbol = cfp.get("general", "spacer_symbol")

    # Get a list of the chosen display options
    display_options: list[DisplayOption] = []
    display_options_str: str = cfp.get("general", "display")
    if display_options_str:
        raw_options = display_options_str.split(",")

        def is_display_option(s: str) -> TypeGuard[DisplayOption]:
            return s in DEFAULT_DISPLAY_OPTIONS_FORMAT

        # Validate options and convert to DisplayOption list
        invalid = [opt for opt in raw_options if not is_display_option(opt)]
        if invalid:
            raise WaybarCryptoException(f"invalid display option '{invalid[0]}'")
        display_options = [opt for opt in raw_options if is_display_option(opt)]

    if not display_options:
        display_options = DEFAULT_DISPLAY_OPTIONS

    # Parse global format overrides from [general] section.
    # This mapping can be empty; base defaults (including currency symbol for price)
    # will be applied at render time.
    display_options_format_overrides: dict[DisplayOption, str] = {}
    for display_key in DEFAULT_DISPLAY_OPTIONS_FORMAT:
        format_option = f"{FORMAT_OPTION_PREFIX}{display_key}"
        if cfp.has_option("general", format_option):
            display_options_format_overrides[display_key] = cfp.get("general", format_option)

    config: Config = {
        "general": {
            "api_key": api_key,
            "currency_symbol": currency_symbol,
            "currency": currency,
            "display_options_format": display_options_format_overrides,
            "display_options": display_options,
            "spacer_symbol": spacer_symbol,
        },
        "coins": coins,
    }

    return config
