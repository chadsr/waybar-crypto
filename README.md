# waybar-crypto

[![Build Status](https://travis-ci.org/Chadsr/waybar-crypto.svg?branch=master)](https://travis-ci.org/Chadsr/waybar-crypto)

## A [waybar](https://github.com/Alexays/Waybar) plugin for displaying cryptocurrency market information.

![Example Setup](https://raw.githubusercontent.com/Chadsr/waybar-crypto/master/images/waybar_crypto.png)

### Requirements

- Python 3.6 or greater
- python-requests

### Installation

1. Clone this repo into the waybar modules directory

```
cd ~/.config/waybar/modules
git clone https://github.com/Chadsr/waybar-crypto.git crypto

# If you don't want to install python-requests via your system package manager
pip install --user -r requirements.txt
```

2. Then in your waybar config (e.g. `~/.config/waybar/config`)

```
"custom/crypto": {
    "format": "{}",
    "interval": 600,
    "return-type": "json",
    "exec": "~/.config/waybar/modules/crypto/crypto.py",
    "exec-if": "ping pro-api.coinmarketcap.com -c1"
}
```

3. Install the needed fonts

```
curl -O https://github.com/AllienWorks/cryptocoins/blob/master/webfont/cryptocoins.ttf
cp cryptocoins.ttf /usr/share/fonts/TTF # Or some font path of your choice
sudo fc-cache -f -v # Rebuild font cache
```

### Configuration
Copy the example configuration file `config.ini.example` to `config.ini`.

The information displayed can then be customised by editing the `config.ini` configuration file.
(e.g. `~/.config/waybar/modules/crypto/config.ini` if you followed the instructions above)

```
[general]
currency = eur
currency_symbol = €
display = price,change24h,change7d
api_key = some_coinmarketcap_key

[btc]
icon = 
price_precision = 2
change_precision = 2
volume_precision = 2

[eth]
icon = 
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
  - **volume24h:** Displays the volume in your chosen currency, over the past 24 hours.
- **api_key:** CoinmarketCap API key obtained from their [new api](https://coinmarketcap.com/api/) (The public API is discontinuing :'()

_Alternatively, the CoinMarketCap API key can be set through the environment variable `COINMARKETCAP_API_KEY`, if you do not wish to save it to the `config.ini` configuration file._

#### Adding cryptocurrencies:

For each cryptocurrency you wish to display, add a section as shown in the example above, where the section name is the **short** cryptocurrency name.

Valid options:

- **icon:** A character symbol to display next to this cryptocurrency's metrics.
- **price_precision** The decimal precision at which to display the price value of the cryptocurrency.
- **change_precision** The decimal precision at which to display the change value(s) of the cryptocurrency.
- **volume_precision** The decimal precision at which to display the volume value of the cryptocurrency.
