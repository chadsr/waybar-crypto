import os
import pytest

from waybar_crypto import CLASS_NAME, ResponseQuotesLatest, WaybarCrypto


# Get the absolute path of this script
ABS_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = f"{ABS_DIR}/../config.ini.example"


@pytest.fixture()
def waybar_crypto():
    yield WaybarCrypto(CONFIG_PATH)


@pytest.fixture()
def quotes_latest():
    yield {
        "status": {
            "timestamp": "2024-05-20T17:29:45.646Z",
            "error_code": 0,
            "error_message": None,
        },
        "data": {
            "BTC": {
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
                    }
                },
            },
            "ETH": {
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
                    }
                },
            },
        },
    }


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
