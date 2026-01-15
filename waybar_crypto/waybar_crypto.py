from typing import TypedDict

import requests

from .config import DEFAULT_PRECISION, Config
from .exceptions import CoinmarketcapApiException, NoApiKeyException, WaybarCryptoException

API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

CLASS_NAME = "crypto"
TIMEOUT_SECONDS = 10


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


class WaybarCrypto(object):
    def __init__(self, config: Config):
        if config["general"]["api_key"] == "":
            raise NoApiKeyException("No API key provided")

        self.config: Config = config

    def _find_coin_data(self, data: dict[str, QuoteData], symbol: str) -> QuoteData:
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
            coin_data = self._find_coin_data(quotes_latest["data"], coin_name)
            pair_info = coin_data["quote"][currency]

            output = f"{icon}"

            # Get per-coin format overrides if available
            coin_format_overrides = coin_config.get("display_options_format", {})

            for display_option in display_options:
                precision = DEFAULT_PRECISION
                if "volume" in display_option:
                    precision = volume_precision
                elif "change" in display_option:
                    precision = change_precision
                elif "price" in display_option:
                    precision = price_precision

                value = round(pair_info[display_option], precision)
                # Use per-coin format if available, otherwise use global format
                format_str = coin_format_overrides.get(
                    display_option, display_options_format[display_option]
                )
                output += f" {format_str}".format(dp=precision, val=value)

            if coin_config["in_tooltip"]:
                if output_obj["tooltip"] != "":
                    output = f"\n{output}"
                output_obj["tooltip"] += output
            else:
                if output_obj["text"] != "":
                    output = f"{spacer} {output}"
                output_obj["text"] += output

        return output_obj
