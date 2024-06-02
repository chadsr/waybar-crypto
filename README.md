# waybar-crypto

[![Tests](https://github.com/chadsr/waybar-crypto/actions/workflows/test.yml/badge.svg)](https://github.com/chadsr/waybar-crypto/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/chadsr/waybar-crypto/graph/badge.svg?token=DBLYX5C0ST)](https://codecov.io/gh/chadsr/waybar-crypto)
![AUR Version](https://img.shields.io/aur/version/waybar-crypto)

A [Waybar](https://github.com/Alexays/Waybar) module for displaying cryptocurrency market information, utilising the [CoinMarketCap API](https://coinmarketcap.com/api/documentation/v1/).

![Example Setup](https://raw.githubusercontent.com/chadsr/waybar-crypto/master/images/waybar_crypto.png)

## Requirements

- `python` >=3.10
- `python-requests`

## Installation

### [AUR](https://aur.archlinux.org/packages/waybar-crypto)

```shell
yay -S waybar-crypto
```

**Note:** *For the time being, the `cryptofont` font still needs installing manually*

### (Or) Clone to the Waybar modules directory

```shell
cd ~/.config/waybar/modules
git clone https://github.com/chadsr/waybar-crypto.git crypto && cd crypto/
git submodule update --init --recursive --remote --progress
```

### Install the needed fonts

```shell
 # Use ~/.local/share/fonts/TTF (user scope, recommended) or /usr/share/fonts/TTF (system scope)
mkdir -p ~/.local/share/fonts/TTF
ln -s ./.submodules/cryptofont/fonts/cryptofont.ttf ~/.local/share/fonts/TTF

# Rebuild font cache
fc-cache -f
```

### Create Configuration File

Create a configuration file at `$XDG_CONFIG_HOME/waybar-crypto/config.ini` (This location can be customised with the `--config-path` flag). The module **will not** run without first creating this configuration file.

An example can be found in [`config.ini.example`](./config.ini.example) with further options described below in the [Configuration](#configuration) section.


### Update Waybar Configuration

*Found at `~/.config/waybar/config` by default*

```json
"custom/crypto": {
    "format": "{}",
    "interval": 600,
    "return-type": "json",
    "exec": "waybar-crypto", // change this if you installed manually
    "exec-if": "ping pro-api.coinmarketcap.com -c1"
}
```

### Style the module

*Found at `~/.config/waybar/style.css` by default*

```css
#custom-crypto {
    font-family: cryptofont;
}
```

## Configuration

- **currency:** A valid currency code
- **currency_symbol:** A corresponding symbol of the currency you wish to display
- **spacer_symbol:** A string/character to use as a spacer between tickers. Comment out to disable
- **display:** A list of metrics you wish to display for each crypto currency. No spaces.
  Valid options are:
  - **price:** current price
  - **percent_change_1h:** Price change over the past hour
  - **percent_change_24h:** Price change over the past 24 hours
  - **percent_change_7d:** Price change over the past week
  - **percent_change_30d:** Price change over the past thirty days
  - **percent_change_60d:** Price change over the past sixty days
  - **percent_change_90d:** Price change over the past ninety days
  - **volume_24h:** Market volume in your chosen currency, over the past 24 hours
  - **volume_change_24h:** Market volume change in your chosen currency, over the past 24 hours
- **api_key:** CoinmarketCap API key obtained from their [API Dashboard](https://coinmarketcap.com/api)

  *Alternatively, the CoinMarketCap API key can be set through the environment variable `COINMARKETCAP_API_KEY`, if you do not wish to save it to the `config.ini` configuration file.*

### Adding Cryptocurrencies

For each cryptocurrency you wish to display, add a section as shown in the [example file](./config.ini.example), where the section name is the **short** cryptocurrency name as found on [CoinMarketCap](https://coinmarketcap.com/).

Valid options:

- **icon:** A character symbol to display next to this cryptocurrency's metrics
- **in_tooltip:** Whether to display the data in the tooltip instead of the bar (defaults to false)
- **price_precision** The decimal precision at which to display the price value of the cryptocurrency
- **change_precision** The decimal precision at which to display the change value(s) of the cryptocurrency
- **volume_precision** The decimal precision at which to display the volume value of the cryptocurrency
