# waybar-crypto

[![Tests](https://github.com/chadsr/waybar-crypto/actions/workflows/test.yml/badge.svg)](https://github.com/chadsr/waybar-crypto/actions/workflows/test.yml)

A [Waybar](https://github.com/Alexays/Waybar) module for displaying cryptocurrency market information, utilising the [CoinMarketCap API](https://coinmarketcap.com/api/documentation/v1/).

![Example Setup](https://raw.githubusercontent.com/chadsr/waybar-crypto/master/images/waybar_crypto.png)

## Requirements

- `python` >=3.8
- `python-requests`

## Installation

### Clone to the Waybar modules directory

```shell
cd ~/.config/waybar/modules
git clone https://github.com/chadsr/waybar-crypto.git crypto && cd crypto/
git submodule update --init --recursive --remote --progress

# **only** If you for some reason don't want to install python-requests with a package manager, or setup a venv
pip install --user --requirement <(poetry export --without=dev --format requirements.txt)
```

### Install the needed fonts

```shell
 # Use ~/.local/share/fonts/TTF (user scope, recommended) or /usr/share/fonts/TTF (system scope)
mkdir -p ~/.local/share/fonts/TTF
ln -s ./.submodules/cryptocoins/webfont/cryptocoins.ttf ~/.local/share/fonts/TTF

# Rebuild font cache
fc-cache -f
```

### Update Waybar configuration

*Found at `~/.config/waybar/config` by default*

```json
"custom/crypto": {
    "format": "{}",
    "interval": 600,
    "return-type": "json",
    "exec": "~/.config/waybar/modules/crypto/waybar_crypto.py",
    "exec-if": "ping pro-api.coinmarketcap.com -c1"
}
```

### Style the module

*Found at `~/.config/waybar/style.css` by default*

```css
#custom-crypto {
    font-family: cryptocoins, monospace;
}
```

## Configuration

Copy the example configuration file `config.ini.example` to `config.ini`.

The information displayed can then be customised by editing the `config.ini` configuration file.
(e.g. `~/.config/waybar/modules/crypto/config.ini` if you followed the instructions above)

```ini
[general]
currency = eur
currency_symbol = €
display = price,change24h,change7d
api_key = your_coinmarketcap_api_key

[btc]
icon = 
price_precision = 2
change_precision = 2
volume_precision = 2

[eth]
icon = 
price_precision = 2
change_precision = 2
volume_precision = 2
```

- **currency:** Any valid currency code should be accepted
- **currency_symbol:** A corresponding symbol of the currency you wish to display
- **display:** A list of metrics you wish to display for each crypto currency. No spaces.
  Valid options are:
  - **price:** Displays the current price.
  - **change1h:** Displays the price change over the past hour.
  - **change24h:** Displays the price change over the past 24 hours.
  - **change7d:** Displays the price change over the past week.
  - **change30d:** Displays the price change over the past month.
  - **volume24h:** Displays the volume in your chosen currency, over the past 24 hours.
- **api_key:** CoinmarketCap API key obtained from their [API Dashboard](https://coinmarketcap.com/api).

*Alternatively, the CoinMarketCap API key can be set through the environment variable `COINMARKETCAP_API_KEY`, if you do not wish to save it to the `config.ini` configuration file.*

### Adding Cryptocurrencies

For each cryptocurrency you wish to display, add a section as shown in the example above, where the section name is the **short** cryptocurrency name as found on [CoinMarketCap](https://coinmarketcap.com/).

Valid options:

- **icon:** A character symbol to display next to this cryptocurrency's metrics.
- **price_precision** The decimal precision at which to display the price value of the cryptocurrency.
- **change_precision** The decimal precision at which to display the change value(s) of the cryptocurrency.
- **volume_precision** The decimal precision at which to display the volume value of the cryptocurrency.
