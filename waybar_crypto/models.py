from collections.abc import Mapping
from typing import TypedDict, Literal


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


DisplayOption = Literal[
    "price",
    "percent_change_1h",
    "percent_change_24h",
    "percent_change_7d",
    "percent_change_30d",
    "percent_change_60d",
    "percent_change_90d",
    "volume_24h",
    "volume_change_24h",
]

DisplayOptionsFormatMap = Mapping[DisplayOption, str]
