from typing import cast
import requests
from collections.abc import Mapping

from .config import DEFAULT_PRECISION, DEFAULT_DISPLAY_OPTIONS_FORMAT, Config
from .exceptions import CoinmarketcapApiException, NoApiKeyException, WaybarCryptoException
from .models import (
    ResponseQuotesLatest,
    WaybarOutput,
    QuoteData,
)

API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
TIMEOUT_SECONDS = 10

WAYBAR_CLASS_NAME = "crypto"


class WaybarCrypto(object):
    def __init__(self, config: Config):
        if config["general"]["api_key"] == "":
            raise NoApiKeyException("No API key provided")

        self.config: Config = config

    def _find_coin_data(self, data: Mapping[str, QuoteData], symbol: str) -> QuoteData:
        """Find coin data with case-insensitive symbol matching.

        The CoinMarketCap API may return data keyed by a symbol with different
        casing than what was requested (e.g., 'XAUt' vs 'XAUT'). This method
        handles such cases by performing a case-insensitive lookup.

        Args:
            data: The API response data dict keyed by symbol
            symbol: The symbol to look up

        Returns:
            The QuoteData for the matching symbol

        Raises:
            WaybarCryptoException: If the symbol is not found in the response
        """
        # Try exact match first (most common case)
        if symbol in data:
            return data[symbol]

        # Fallback to case-insensitive match
        symbol_lower = symbol.lower()
        for key, value in data.items():
            if key.lower() == symbol_lower:
                return value

        raise WaybarCryptoException(f"symbol '{symbol}' not found in API response")

    def coinmarketcap_latest(self) -> ResponseQuotesLatest:
        # Construct API query parameters
        params = {
            "convert": self.config["general"]["currency"].upper(),
            "symbol": ",".join(self.config["coins"]),  # Preserve original case
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
            response_quotes_latest: ResponseQuotesLatest = cast(
                ResponseQuotesLatest, response.json()
            )
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
        currency_symbol = self.config["general"]["currency_symbol"]
        display_options = self.config["general"]["display_options"]
        # Global overrides may be absent or empty; merge with defaults at render time
        global_overrides = dict(self.config["general"].get("display_options_format", {}))
        spacer = self.config["general"]["spacer_symbol"]
        if spacer != "":
            spacer = f" {spacer}"

        output_obj: WaybarOutput = {
            "text": "",
            "tooltip": "",
            "class": WAYBAR_CLASS_NAME,
        }

        # For each coin, populate our output_obj
        # with a string according to the display_options
        for coin_name, coin_config in self.config["coins"].items():
            icon = coin_config["icon"]

            price_precision = coin_config["price_precision"]
            volume_precision = coin_config["volume_precision"]
            change_precision = coin_config["change_precision"]

            coin_data = self._find_coin_data(quotes_latest["data"], coin_name)
            pair_info = coin_data["quote"][currency]

            output = f"{icon}"

            # Build merged format map: defaults -> add currency symbol -> global overrides -> per-coin overrides
            merged_format = DEFAULT_DISPLAY_OPTIONS_FORMAT.copy()
            merged_format["price"] = f"{currency_symbol}{merged_format['price']}"
            for k, v in global_overrides.items():
                merged_format[k] = v
            coin_format_overrides = dict(coin_config.get("display_options_format", {}))
            for k, v in coin_format_overrides.items():
                merged_format[k] = v

            for display_option in display_options:
                precision = DEFAULT_PRECISION
                if "volume" in display_option:
                    precision = volume_precision
                elif "change" in display_option:
                    precision = change_precision
                elif "price" in display_option:
                    precision = price_precision

                value = round(pair_info[display_option], precision)
                format_str = merged_format[display_option]
                output += f" {format_str}".format(dp=precision, val=value)

            if coin_config.get("in_tooltip", False):
                if output_obj["tooltip"] != "":
                    output = f"\n{output}"
                output_obj["tooltip"] += output
            else:
                if output_obj["text"] != "":
                    output = f"{spacer} {output}"
                output_obj["text"] += output
        if outout_obj["text"] == "":
            for coin_name, coin_config in self.config["coins"].items():
                output_obj["text"] += coin_config["icon"]
            

        return output_obj
