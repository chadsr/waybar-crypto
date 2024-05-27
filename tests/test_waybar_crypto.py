import os
import argparse
import pytest
from unittest import mock

from waybar_crypto import (
    API_KEY_ENV,
    CLASS_NAME,
    DEFAULT_DISPLAY_OPTIONS_FORMAT,
    DEFAULT_XDG_CONFIG_HOME_PATH,
    XDG_CONFIG_HOME_ENV,
    Config,
    NoApiKeyException,
    ResponseQuotesLatest,
    WaybarCrypto,
    parse_args,
    read_config,
)


# Get the absolute path of this script
ABS_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_CONFIG_PATH = "/test_path"
TEST_API_KEY = "test_key"


@pytest.fixture()
def config() -> Config:
    return {
        "general": {
            "currency": "eur",
            "currency_symbol": "€",
            "spacer_symbol": "|",
            "display_options": [],
            "display_options_format": DEFAULT_DISPLAY_OPTIONS_FORMAT,
            "api_key": "test_key",
        },
        "coins": {
            "btc": {
                "icon": "BTC",
                "in_tooltip": False,
                "price_precision": 1,
                "change_precision": 2,
                "volume_precision": 2,
            },
            "eth": {
                "icon": "ETH",
                "in_tooltip": False,
                "price_precision": 2,
                "change_precision": 2,
                "volume_precision": 2,
            },
            "dot": {
                "icon": "DOT",
                "in_tooltip": True,
                "price_precision": 4,
                "change_precision": 2,
                "volume_precision": 2,
            },
            "avax": {
                "icon": "AVAX",
                "in_tooltip": True,
                "price_precision": 3,
                "change_precision": 2,
                "volume_precision": 2,
            },
        },
    }


@pytest.fixture()
def waybar_crypto(config: Config) -> WaybarCrypto:
    return WaybarCrypto(config)


@pytest.fixture()
def quotes_latest() -> ResponseQuotesLatest:
    return {
        "status": {
            "timestamp": "2024-05-20T17:29:45.646Z",
            "error_code": 0,
            "error_message": "",
            "elapsed": 5,
            "credit_count": 1,
        },
        "data": {
            "BTC": {
                "id": 1,
                "name": "Bitcoin",
                "symbol": "BTC",
                "quote": {
                    "EUR": {
                        "price": 62885.47621569202,
                        "volume_24h": 25044422439.850758,
                        "volume_change_24h": 60.5157,
                        "percent_change_1h": 0.88305833,
                        "percent_change_24h": 2.3000565,
                        "percent_change_7d": 8.88835578,
                        "percent_change_30d": 4.71056688,
                        "percent_change_60d": 3.13017816,
                        "percent_change_90d": 33.96699196,
                        "last_updated": "2024-05-27T12:58:04.000Z",
                    }
                },
            },
            "ETH": {
                "id": 1027,
                "name": "Ethereum",
                "symbol": "ETH",
                "quote": {
                    "EUR": {
                        "price": 2891.33408409618,
                        "volume_24h": 11289361021.62208,
                        "volume_change_24h": 50.8811,
                        "percent_change_1h": 0.56650814,
                        "percent_change_24h": 2.18445121,
                        "percent_change_7d": 6.56024063,
                        "percent_change_30d": 0.04147897,
                        "percent_change_60d": -10.18412449,
                        "percent_change_90d": 8.36092599,
                        "last_updated": "2024-05-27T12:58:04.000Z",
                    }
                },
            },
            "AVAX": {
                "id": 5805,
                "name": "Avalanche",
                "symbol": "AVAX",
                "quote": {
                    "EUR": {
                        "price": 34.15081432131667,
                        "volume_24h": 206005212.6801803,
                        "volume_change_24h": -21.5639,
                        "percent_change_1h": -0.1101364,
                        "percent_change_24h": -2.21628843,
                        "percent_change_7d": 2.46514204,
                        "percent_change_30d": 3.78312279,
                        "percent_change_60d": -30.74974196,
                        "percent_change_90d": -0.83220421,
                        "last_updated": "2024-05-27T12:58:04.000Z",
                    }
                },
            },
            "DOT": {
                "id": 6636,
                "name": "Polkadot",
                "symbol": "DOT",
                "quote": {
                    "EUR": {
                        "price": 6.9338115798384905,
                        "volume_24h": 145060142.27706677,
                        "volume_change_24h": 0.3964,
                        "percent_change_1h": 0.59467025,
                        "percent_change_24h": 3.37180336,
                        "percent_change_7d": 7.19067559,
                        "percent_change_30d": 8.73368475,
                        "percent_change_60d": -19.8413195,
                        "percent_change_90d": -2.24744556,
                        "last_updated": "2024-05-27T12:58:04.000Z",
                    }
                },
            },
        },
    }


def test_parse_args_default_path():
    with mock.patch("sys.argv", ["waybar_crypto.py"]):
        os.environ[XDG_CONFIG_HOME_ENV] = ""
        args = parse_args()
        assert "config_path" in args
        assert os.path.expanduser(DEFAULT_XDG_CONFIG_HOME_PATH) in os.path.expanduser(
            args["config_path"]
        )


def test_parse_args_custom_xdg_data_home():
    with mock.patch("sys.argv", ["waybar_crypto.py"]):
        os.environ[XDG_CONFIG_HOME_ENV] = TEST_CONFIG_PATH
        args = parse_args()
        assert "config_path" in args
        assert TEST_CONFIG_PATH in args["config_path"]


@mock.patch(
    "argparse.ArgumentParser.parse_args",
    return_value=argparse.Namespace(config_path=TEST_CONFIG_PATH),
)
def test_parse_args_custom_path(mock: mock.MagicMock):
    args = parse_args()
    assert "config_path" in args
    assert args["config_path"] == TEST_CONFIG_PATH


@mock.patch.dict(os.environ, {API_KEY_ENV: ""})
def test_read_config(mock: mock.MagicMock):
    config = read_config(TEST_CONFIG_PATH)

    assert "general" in config
    general = config["general"]
    assert isinstance(general, dict)
    assert "currency" in general
    assert "currency_symbol" in general
    assert "spacer_symbol" in general
    assert "display_options" in general
    assert "display_options_format" in general
    assert "api_key" in general

    assert "coins" in config
    coins = config["coins"]
    assert isinstance(coins, dict)


@mock.patch.dict(os.environ, {API_KEY_ENV: TEST_API_KEY})
def test_read_config_env(mock: mock.MagicMock):
    config = read_config(TEST_CONFIG_PATH)

    assert config["general"]["api_key"] == TEST_API_KEY


class TestWaybarCrypto:
    """Tests for the WaybarCrypto."""

    def test_get_coinmarketcap_latest(self, waybar_crypto: WaybarCrypto):
        resp_quotes_latest = waybar_crypto.coinmarketcap_latest()
        assert isinstance(resp_quotes_latest, dict)

        resp_fields = ["status", "data"]
        for field in resp_fields:
            assert field in resp_quotes_latest
            assert isinstance(resp_quotes_latest[field], dict)

        for coin_data in resp_quotes_latest["data"].values():
            assert "quote" in coin_data
            quote = coin_data["quote"]
            assert isinstance(quote, dict)

            quote_fields_types = {
                "price": float,
                "volume_24h": float,
                "volume_change_24h": float,
                "percent_change_1h": float,
                "percent_change_24h": float,
                "percent_change_7d": float,
                "percent_change_30d": float,
                "percent_change_60d": float,
                "percent_change_90d": float,
            }

            for quote_values in quote.values():
                for field, field_type in quote_fields_types.items():
                    assert field in quote_values
                    assert isinstance(quote_values[field], field_type)

    def test_waybar_output(self, waybar_crypto: WaybarCrypto, quotes_latest: ResponseQuotesLatest):
        output = waybar_crypto.waybar_output(quotes_latest)
        assert isinstance(output, dict)
        fields = ["text", "tooltip", "class"]
        for field in fields:
            assert field in output
            assert isinstance(output[field], str)

        assert output["class"] == CLASS_NAME

    @mock.patch.dict(os.environ, {API_KEY_ENV: ""})
    def test_no_api_key(self, config: Config):
        try:
            config["general"]["api_key"] = ""
            _ = WaybarCrypto(config)
        except Exception as e:
            assert isinstance(e, NoApiKeyException)
