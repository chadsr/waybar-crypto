import os
import json

from waybar_crypto import WaybarCrypto


class TestWaybarCrypto:
    """Tests for the WaybarCrypto."""

    def test_get_json(self):
        # Get the absolute path of this script
        abs_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = f"{abs_dir}/../config.ini.example"

        waybar_crypto = WaybarCrypto(config_path)

        result_json = waybar_crypto.get_json()
        assert isinstance(result_json, str)

        result = json.loads(result_json)
        assert result["text"] and len(result["text"]) > 0
        assert result["class"] == "crypto"
