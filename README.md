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
```

### Configuration
The information displayed can be customised by editing the crypto.ini configuration file.
(e.g. `~/.config/waybar/modules/crypto/crypto.ini` if you followed the instructions above)

```
[general]
currency = eur
currency_symbol = €
display = price,change24h,change7d
api_key = some_coinmarketcap_key

[btc]
icon = 

[eth]
icon = 
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

#### Adding cryptocurrencies:
For each cryptocurrency you wish to display, add a section as shown in the example above, where the section name is the **short** cryptocurrency name. 

Valid options:
- **icon:** A character symbol to display next to this cryptocurrency's metrics.
